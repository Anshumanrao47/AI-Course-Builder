"""
Analytics endpoint: time-series data for the Recharts dashboard —
completion trend, quiz scores over time, learning consistency (daily
activity), and strong/weak topics.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.progress import compute_completion
from app.database.session import get_db
from app.models.analytics import LearningAnalytics
from app.models.course import Course
from app.models.module import Module
from app.models.progress import UserProgress
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.schemas.progress import AnalyticsPoint, AnalyticsRead, QuizScorePoint

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/{course_id}", response_model=AnalyticsRead)
def get_analytics(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalyticsRead:
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == current_user.id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    daily_rows = (
        db.query(LearningAnalytics)
        .filter(LearningAnalytics.user_id == current_user.id, LearningAnalytics.course_id == course.id)
        .order_by(LearningAnalytics.date)
        .all()
    )

    quiz_attempts = (
        db.query(QuizAttempt, Quiz, Module)
        .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
        .join(Module, Quiz.module_id == Module.id)
        .filter(QuizAttempt.user_id == current_user.id, Module.course_id == course.id)
        .order_by(QuizAttempt.submitted_at)
        .all()
    )

    weak_topic_counts: dict[str, int] = {}
    for attempt, _quiz, _module in quiz_attempts:
        for topic in attempt.weak_topics:
            weak_topic_counts[topic] = weak_topic_counts.get(topic, 0) + 1
    weak_topics = sorted(weak_topic_counts, key=weak_topic_counts.get, reverse=True)[:5]

    _completed_ids, _total, completion_percentage = compute_completion(db, current_user.id, course.id)

    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id, UserProgress.course_id == course.id)
        .first()
    )

    return AnalyticsRead(
        daily=[
            AnalyticsPoint(
                date=row.date,
                lessons_completed=row.lessons_completed,
                quizzes_taken=row.quizzes_taken,
                avg_quiz_score=row.avg_quiz_score,
            )
            for row in daily_rows
        ],
        quiz_scores=[
            QuizScorePoint(
                submitted_at=attempt.submitted_at.isoformat(),
                module_title=module.title,
                score=attempt.score,
            )
            for attempt, _quiz, module in quiz_attempts
        ],
        strong_topics=course.strengths or [],
        weak_topics=weak_topics or (course.weaknesses or []),
        completion_percentage=completion_percentage,
        current_streak_days=progress.streak_days if progress else 0,
    )
