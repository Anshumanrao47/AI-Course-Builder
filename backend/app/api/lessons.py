"""
Lesson endpoints: read a lesson (generating its content on first read),
and mark a lesson complete (which unlocks the next lesson/module, creates
that module's quiz, and updates progress + analytics).
"""
import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.agents.content_agent import generate_lesson_content
from app.api.deps import get_current_user
from app.core.ai_client import AIGenerationError
from app.database.session import get_db
from app.models.analytics import LearningAnalytics
from app.models.course import Course
from app.models.enums import LessonStatus, ModuleStatus
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.progress import UserProgress
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.lesson import LessonCompleteResponse, LessonRead

router = APIRouter(prefix="/lessons", tags=["lessons"])


def _get_owned_lesson(db: Session, lesson_id: uuid.UUID, user: User) -> tuple[Lesson, Module, Course]:
    lesson = (
        db.query(Lesson)
        .options(joinedload(Lesson.module).joinedload(Module.course))
        .filter(Lesson.id == lesson_id)
        .first()
    )
    if lesson is None or lesson.module.course.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return lesson, lesson.module, lesson.module.course


def _get_or_create_progress(db: Session, user_id: uuid.UUID, course_id: uuid.UUID) -> UserProgress:
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.course_id == course_id)
        .first()
    )
    if progress is None:
        progress = UserProgress(user_id=user_id, course_id=course_id, completed_lesson_ids=[])
        db.add(progress)
        db.flush()
    return progress


def _record_daily_activity(
    db: Session, user_id: uuid.UUID, course_id: uuid.UUID, *, lesson_completed: bool = False
) -> LearningAnalytics:
    today = date.today()
    row = (
        db.query(LearningAnalytics)
        .filter(
            LearningAnalytics.user_id == user_id,
            LearningAnalytics.course_id == course_id,
            LearningAnalytics.date == today,
        )
        .first()
    )
    if row is None:
        row = LearningAnalytics(
            user_id=user_id, course_id=course_id, date=today,
            lessons_completed=0, quizzes_taken=0,
        )
        db.add(row)
        db.flush()
    if lesson_completed:
        row.lessons_completed += 1
    return row


@router.get("/{lesson_id}", response_model=LessonRead)
def get_lesson(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Lesson:
    lesson, module, course = _get_owned_lesson(db, lesson_id, current_user)

    if not lesson.content_generated:
        try:
            content = generate_lesson_content(
                course_topic=course.topic,
                module_title=module.title,
                lesson_title=lesson.title,
                skill_level=course.assessed_skill_level or course.current_level,
                learning_style=course.preferred_learning_style,
            )
        except AIGenerationError as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

        lesson.objectives = content.objectives
        lesson.explanation = content.explanation
        lesson.examples = content.examples
        lesson.exercise = content.exercise
        lesson.summary = content.summary
        lesson.content_generated = True
        db.commit()
        db.refresh(lesson)

    return lesson


@router.post("/{lesson_id}/complete", response_model=LessonCompleteResponse)
def complete_lesson(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LessonCompleteResponse:
    lesson, module, course = _get_owned_lesson(db, lesson_id, current_user)

    if lesson.status == LessonStatus.locked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lesson is locked.")

    already_completed = lesson.status == LessonStatus.completed
    lesson.status = LessonStatus.completed

    # Unlock the next lesson in this module, if any.
    next_lesson = (
        db.query(Lesson)
        .filter(Lesson.module_id == module.id, Lesson.order_index == lesson.order_index + 1)
        .first()
    )
    if next_lesson and next_lesson.status == LessonStatus.locked:
        next_lesson.status = LessonStatus.unlocked

    module_completed = next_lesson is None
    quiz_id: uuid.UUID | None = None

    if module_completed:
        module.status = ModuleStatus.completed

        quiz = db.query(Quiz).filter(Quiz.module_id == module.id).first()
        if quiz is None:
            quiz = Quiz(module_id=module.id, title=f"{module.title} Quiz")
            db.add(quiz)
            db.flush()
        quiz_id = quiz.id

        # Unlock the first lesson of the next module, if any.
        next_module = (
            db.query(Module)
            .filter(Module.course_id == course.id, Module.order_index == module.order_index + 1)
            .first()
        )
        if next_module:
            if next_module.status == ModuleStatus.locked:
                next_module.status = ModuleStatus.unlocked
            first_lesson = (
                db.query(Lesson)
                .filter(Lesson.module_id == next_module.id, Lesson.order_index == 0)
                .first()
            )
            if first_lesson and first_lesson.status == LessonStatus.locked:
                first_lesson.status = LessonStatus.unlocked

    if not already_completed:
        progress = _get_or_create_progress(db, current_user.id, course.id)
        completed_ids = set(progress.completed_lesson_ids or [])
        completed_ids.add(str(lesson.id))
        progress.completed_lesson_ids = list(completed_ids)
        progress.current_module_id = module.id

        today = date.today()
        if progress.last_activity_date == today - timedelta(days=1):
            progress.streak_days += 1
        elif progress.last_activity_date != today:
            progress.streak_days = 1
        progress.last_activity_date = today

        _record_daily_activity(db, current_user.id, course.id, lesson_completed=True)

    db.commit()
    db.refresh(lesson)

    return LessonCompleteResponse(
        lesson=lesson,
        module_completed=module_completed,
        quiz_id=quiz_id,
        next_lesson_id=next_lesson.id if next_lesson else None,
    )
