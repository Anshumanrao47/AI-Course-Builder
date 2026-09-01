"""
Pydantic schemas for progress and analytics.
"""
import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class ProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: uuid.UUID
    current_module_id: uuid.UUID | None
    completed_lesson_ids: list[str]
    total_lessons: int
    completion_percentage: float
    streak_days: int
    last_activity_date: date | None


class AnalyticsPoint(BaseModel):
    date: date
    lessons_completed: int
    quizzes_taken: int
    avg_quiz_score: float | None


class QuizScorePoint(BaseModel):
    submitted_at: str
    module_title: str
    score: float


class AnalyticsRead(BaseModel):
    daily: list[AnalyticsPoint]
    quiz_scores: list[QuizScorePoint]
    strong_topics: list[str]
    weak_topics: list[str]
    completion_percentage: float
    current_streak_days: int
