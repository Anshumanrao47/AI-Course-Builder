"""
Progress endpoint: completion percentage, streak, and current position for
a course.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.progress import UserProgress
from app.models.user import User
from app.schemas.progress import ProgressRead

router = APIRouter(prefix="/progress", tags=["progress"])


def compute_completion(db: Session, user_id: uuid.UUID, course_id: uuid.UUID) -> tuple[list[str], int, float]:
    """Returns (completed_lesson_ids, total_lessons, completion_percentage)."""
    total_lessons = (
        db.query(Lesson).join(Module, Lesson.module_id == Module.id)
        .filter(Module.course_id == course_id).count()
    )
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.course_id == course_id)
        .first()
    )
    completed_ids = progress.completed_lesson_ids if progress else []
    completion_percentage = round(100 * len(completed_ids) / total_lessons, 1) if total_lessons else 0.0
    return completed_ids, total_lessons, completion_percentage


@router.get("/{course_id}", response_model=ProgressRead)
def get_progress(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressRead:
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == current_user.id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    completed_ids, total_lessons, completion_percentage = compute_completion(db, current_user.id, course.id)

    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id, UserProgress.course_id == course.id)
        .first()
    )

    return ProgressRead(
        course_id=course.id,
        current_module_id=progress.current_module_id if progress else None,
        completed_lesson_ids=completed_ids,
        total_lessons=total_lessons,
        completion_percentage=completion_percentage,
        streak_days=progress.streak_days if progress else 0,
        last_activity_date=progress.last_activity_date if progress else None,
    )
