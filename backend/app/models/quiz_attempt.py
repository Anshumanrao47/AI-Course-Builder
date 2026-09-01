"""
QuizAttempt model — one row per submission, holding the Evaluation Agent's
output (score, weak topics, recommendation) alongside the raw answers.
"""
import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime, Float, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    answers: Mapped[dict] = mapped_column(JSON, nullable=False)  # {question_id: answer}
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    weak_topics: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False, default="")

    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    quiz: Mapped["Quiz"] = relationship(back_populates="attempts")
