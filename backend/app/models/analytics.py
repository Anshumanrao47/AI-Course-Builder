"""
LearningAnalytics model — a daily rollup row per (user, course, date), used
to power the Recharts analytics dashboard (Phase 8): progress trends and
learning consistency without re-aggregating raw events on every request.
"""
import uuid
from datetime import date, datetime

from sqlalchemy import DateTime, Date, Integer, Float, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class LearningAnalytics(Base):
    __tablename__ = "learning_analytics"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", "date", name="uq_analytics_user_course_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)

    lessons_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quizzes_taken: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_quiz_score: Mapped[float | None] = mapped_column(Float, nullable=True)
