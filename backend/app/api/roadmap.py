"""
Roadmap endpoints: reading a course's generated modules/lessons, and
manually re-running the Adaptive Learning Agent's recommendation for
whichever module the learner most recently took a quiz on (the automatic
version already runs — and applies its changes — inside
POST /quizzes/{id}/submit; this is the on-demand "what does the agent
recommend right now" version called out in the spec).
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.adaptive_agent import adapt_roadmap
from app.api.deps import get_current_user
from app.core.ai_client import AIGenerationError
from app.database.session import get_db
from app.models.course import Course
from app.models.module import Module
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.schemas.roadmap_adapt import RoadmapAdaptRequest, RoadmapAdaptResponse

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post("/adapt", response_model=RoadmapAdaptResponse)
def adapt(
    payload: RoadmapAdaptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RoadmapAdaptResponse:
    course = db.query(Course).filter(Course.id == payload.course_id, Course.user_id == current_user.id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    latest = (
        db.query(QuizAttempt, Quiz, Module)
        .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
        .join(Module, Quiz.module_id == Module.id)
        .filter(QuizAttempt.user_id == current_user.id, Module.course_id == course.id)
        .order_by(QuizAttempt.submitted_at.desc())
        .first()
    )
    if latest is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No quiz attempts yet — there's nothing to base a roadmap adjustment on.",
        )
    attempt, _quiz, module = latest

    next_module = (
        db.query(Module)
        .filter(Module.course_id == course.id, Module.order_index == module.order_index + 1)
        .first()
    )

    try:
        plan = adapt_roadmap(
            module_title=module.title,
            next_module_title=next_module.title if next_module else None,
            score=attempt.score,
            weak_topics=attempt.weak_topics,
        )
    except AIGenerationError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    return RoadmapAdaptResponse(
        next_action=plan.next_action,
        message=plan.message,
        based_on_module=module.title,
        based_on_score=attempt.score,
    )
