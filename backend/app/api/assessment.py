"""
Assessment endpoints: generate a diagnostic quiz for a course's topic,
then evaluate the answers and generate the course's roadmap in one step
(see agents/graphs.py — evaluate_assessment -> plan_roadmap).
"""
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.assessment_agent import generate_assessment_questions
from app.agents.graphs import run_planning_graph
from app.api.deps import get_current_user
from app.core.ai_client import AIGenerationError
from app.core.security import create_signed_payload_token, decode_signed_payload_token
from app.database.session import get_db
from app.models.course import Course
from app.models.enums import CourseStatus, LessonStatus, ModuleStatus
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.user import User
from app.schemas.assessment import (
    AssessmentAnswerIn,
    AssessmentStartResponse,
    AssessmentQuestionPublic,
    AssessmentSubmitRequest,
    AssessmentSubmitResponse,
)

router = APIRouter(prefix="/assessment", tags=["assessment"])

ASSESSMENT_TOKEN_TTL_MINUTES = 45


def _get_owned_course(db: Session, course_id: uuid.UUID, user: User) -> Course:
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.post("/start", response_model=AssessmentStartResponse)
def start_assessment(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentStartResponse:
    course = _get_owned_course(db, course_id, current_user)

    if course.status not in (CourseStatus.pending_assessment, CourseStatus.assessing):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course is already {course.status.value}; assessment is only available before a roadmap is generated.",
        )

    try:
        question_set = generate_assessment_questions(course.topic, course.current_level)
    except AIGenerationError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    course.status = CourseStatus.assessing
    db.commit()

    token_payload = {
        "purpose": "assessment",
        "course_id": str(course.id),
        "questions": [q.model_dump() for q in question_set.questions],
    }
    token = create_signed_payload_token(token_payload, expires_minutes=ASSESSMENT_TOKEN_TTL_MINUTES)

    return AssessmentStartResponse(
        assessment_token=token,
        questions=[
            AssessmentQuestionPublic(question=q.question, options=q.options)
            for q in question_set.questions
        ],
    )


@router.post("/submit", response_model=AssessmentSubmitResponse)
def submit_assessment(
    payload: AssessmentSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentSubmitResponse:
    course = _get_owned_course(db, payload.course_id, current_user)

    token_data = decode_signed_payload_token(payload.assessment_token)
    if (
        token_data is None
        or token_data.get("purpose") != "assessment"
        or token_data.get("course_id") != str(course.id)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment session is invalid or expired. Start the assessment again.",
        )

    questions_by_text = {q["question"]: q for q in token_data["questions"]}
    answered: list[dict] = []
    for ans in payload.answers:
        source_q = questions_by_text.get(ans.question)
        if source_q is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Answer references a question that wasn't part of this assessment: {ans.question!r}",
            )
        answered.append({**source_q, "selected_answer": ans.selected_answer})

    if not answered:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No answers submitted.")

    days_available = max((course.target_completion_date - date.today()).days, 1)

    graph_state = {
        "learning_goal": course.topic,
        "current_skill_level": course.current_level.value,
        "target_skill_level": course.target_level.value,
        "preferred_learning_style": course.preferred_learning_style.value,
        "study_minutes_per_day": course.study_minutes_per_day,
        "days_available": days_available,
        "assessment_answers": answered,
    }

    try:
        result = run_planning_graph(graph_state)
    except AIGenerationError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    course.assessed_skill_level = result["assessment_results"]["skill_level"]
    course.strengths = result["strengths"]
    course.weaknesses = result["weaknesses"]
    course.status = CourseStatus.active

    modules_created = 0
    for m_idx, module_data in enumerate(result["course_roadmap"]):
        module = Module(
            course_id=course.id,
            title=module_data["title"],
            order_index=m_idx,
            estimated_minutes=module_data["estimated_minutes"],
            status=ModuleStatus.unlocked if m_idx == 0 else ModuleStatus.locked,
        )
        db.add(module)
        db.flush()  # get module.id before creating lessons
        modules_created += 1

        for l_idx, lesson_data in enumerate(module_data["lessons"]):
            db.add(
                Lesson(
                    module_id=module.id,
                    title=lesson_data["title"],
                    order_index=l_idx,
                    estimated_minutes=lesson_data["estimated_minutes"],
                    status=LessonStatus.unlocked if (m_idx == 0 and l_idx == 0) else LessonStatus.locked,
                )
            )

    db.commit()

    return AssessmentSubmitResponse(
        skill_level=course.assessed_skill_level,
        strengths=course.strengths,
        weaknesses=course.weaknesses,
        modules_created=modules_created,
    )
