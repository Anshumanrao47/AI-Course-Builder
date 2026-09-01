"""
Quiz model — one quiz per module, generated lazily by the Quiz Generation
Agent (Phase 6) the first time a user opens it.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    questions_generated: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    module: Mapped["Module"] = relationship(back_populates="quiz")  # noqa: F821
    questions: Mapped[list["QuizQuestion"]] = relationship(  # noqa: F821
        back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.order_index"
    )
    attempts: Mapped[list["QuizAttempt"]] = relationship(  # noqa: F821
        back_populates="quiz", cascade="all, delete-orphan"
    )
