"""
QuizQuestion model. `correct_answer` is never serialized back to the client
before grading — see schemas/quiz.py.
"""
import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime, Integer, ForeignKey, JSON, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import QuestionType, Difficulty


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), index=True, nullable=False
    )

    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        SAEnum(QuestionType, name="question_type"), nullable=False
    )
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)  # only for multiple_choice
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[str | None] = mapped_column(Text, nullable=True)  # used for weak-topic detection
    difficulty: Mapped[Difficulty] = mapped_column(
        SAEnum(Difficulty, name="difficulty"), nullable=False, default=Difficulty.medium
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")
