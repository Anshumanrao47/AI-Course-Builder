"""
Quiz endpoints: read a quiz (generating its questions on first read), and
submit answers — which runs the adaptive graph (grade -> decide roadmap
changes) and applies any resulting revision lessons.
"""
import difflib
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.agents.graphs import run_adaptive_graph
from app.agents.quiz_agent import generate_quiz
from app.api.deps import get_current_user
from app.api.lessons import _get_or_create_progress, _record_daily_activity
from app.core.ai_client import AIGenerationError
from app.database.session import get_db
from app.models.course import Course
from app.models.enums import LessonStatus, ModuleStatus, QuestionType
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_question import QuizQuestion
from app.models.analytics import LearningAnalytics
from app.models.user import User
from app.schemas.quiz import QuizAttemptRead, QuizRead, QuizSubmitRequest

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


def _get_owned_quiz(db: Session, quiz_id: uuid.UUID, user: User) -> tuple[Quiz, Module, Course]:
    quiz = (
        db.query(Quiz)
        .options(joinedload(Quiz.module).joinedload(Module.course))
        .filter(Quiz.id == quiz_id)
        .first()
    )
    if quiz is None or quiz.module.course.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    return quiz, quiz.module, quiz.module.course


def _is_answer_correct(question: QuizQuestion, given_answer: str) -> bool:
    if question.question_type == QuestionType.multiple_choice:
        return given_answer.strip().lower() == question.correct_answer.strip().lower()
    # Descriptive/coding answers are graded with a similarity heuristic rather
    # than a second LLM call per question — good enough to detect an
    # unattempted or wildly off-base answer, which is what drives weak-topic
    # detection here.
    ratio = difflib.SequenceMatcher(
        None, given_answer.strip().lower(), question.correct_answer.strip().lower()
    ).ratio()
    return ratio >= 0.5


@router.get("/{quiz_id}", response_model=QuizRead)
def get_quiz(
    quiz_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Quiz:
    quiz, module, course = _get_owned_quiz(db, quiz_id, current_user)

    if not quiz.questions_generated:
        lesson_summaries = [
            lesson.summary or lesson.title
            for lesson in sorted(module.lessons, key=lambda l: l.order_index)
        ]
        latest_attempt = (
            db.query(QuizAttempt)
            .filter(QuizAttempt.quiz_id == quiz.id)
            .order_by(QuizAttempt.submitted_at.desc())
            .first()
        )
        try:
            question_set = generate_quiz(
                module_title=module.title,
                lesson_summaries=lesson_summaries,
                recent_avg_score=latest_attempt.score if latest_attempt else None,
            )
        except AIGenerationError as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

        for idx, q in enumerate(question_set.questions):
            db.add(
                QuizQuestion(
                    quiz_id=quiz.id,
                    order_index=idx,
                    question=q.question,
                    question_type=q.question_type,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    topic=q.topic,
                    difficulty=q.difficulty,
                )
            )
        quiz.questions_generated = True
        db.commit()
        db.refresh(quiz)

    return quiz


@router.post("/{quiz_id}/submit", response_model=QuizAttemptRead)
def submit_quiz(
    quiz_id: uuid.UUID,
    payload: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizAttemptRead:
    quiz, module, course = _get_owned_quiz(db, quiz_id, current_user)

    questions_by_id = {q.id: q for q in quiz.questions}
    if not questions_by_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz has no questions yet.")

    graded = []
    answers_record: dict[str, str] = {}
    for ans in payload.answers:
        question = questions_by_id.get(ans.question_id)
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Answer references a question not in this quiz: {ans.question_id}",
            )
        is_correct = _is_answer_correct(question, ans.answer)
        graded.append({"question": question.question, "topic": question.topic or module.title, "is_correct": is_correct})
        answers_record[str(question.id)] = ans.answer

    if len(graded) < len(questions_by_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All questions must be answered.")

    next_module = (
        db.query(Module)
        .filter(Module.course_id == course.id, Module.order_index == module.order_index + 1)
        .first()
    )

    graph_state = {
        "current_module": module.title,
        "_graded": graded,
        "_next_module_title": next_module.title if next_module else None,
        "quiz_scores": [],
        "recommendations": [],
    }

    try:
        result = run_adaptive_graph(graph_state)
    except AIGenerationError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    evaluation = result["_evaluation"]

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=current_user.id,
        answers=answers_record,
        score=evaluation["score"],
        weak_topics=evaluation["weak_topics"],
        recommendation=evaluation["recommendation"],
    )
    db.add(attempt)

    # Apply the Adaptive Learning Agent's decision.
    if result["next_action"] == "revise":
        topics = evaluation["weak_topics"] or [module.title]
        existing_count = len(module.lessons)
        for i, topic in enumerate(topics[:3]):
            db.add(
                Lesson(
                    module_id=module.id,
                    title=f"Revision: {topic}",
                    order_index=existing_count + i,
                    estimated_minutes=20,
                    status=LessonStatus.unlocked if i == 0 else LessonStatus.locked,
                    is_revision=True,
                )
            )
        module.status = ModuleStatus.unlocked

    progress = _get_or_create_progress(db, current_user.id, course.id)
    analytics_row = _record_daily_activity(db, current_user.id, course.id, lesson_completed=False)

    today = date.today()
    analytics_row.quizzes_taken += 1
    prior_scores = [
        a.score
        for a in db.query(QuizAttempt)
        .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
        .join(Module, Quiz.module_id == Module.id)
        .filter(Module.course_id == course.id, QuizAttempt.submitted_at >= today)
        .all()
    ] + [evaluation["score"]]
    analytics_row.avg_quiz_score = sum(prior_scores) / len(prior_scores)

    db.commit()
    db.refresh(attempt)

    return QuizAttemptRead(
        id=attempt.id,
        score=attempt.score,
        weak_topics=attempt.weak_topics,
        recommendation=attempt.recommendation,
        submitted_at=attempt.submitted_at,
        next_action=result["next_action"],
        adaptive_message=result["_adaptive_message"],
    )
