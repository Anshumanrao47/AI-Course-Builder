"""
Lesson model. Content fields start empty and are filled in lazily, on first
read, by the Content Generation Agent (Phase 5) — so course creation and
roadmap generation stay fast, and lessons the user never opens cost nothing.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, JSON, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import LessonStatus


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    status: Mapped[LessonStatus] = mapped_column(
        SAEnum(LessonStatus, name="lesson_status"), nullable=False, default=LessonStatus.locked
    )

    # Generated lazily by the Content Generation Agent; null until first read.
    objectives: Mapped[list | None] = mapped_column(JSON, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    examples: Mapped[list | None] = mapped_column(JSON, nullable=True)
    exercise: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_generated: Mapped[bool] = mapped_column(default=False)

    # Set by the Adaptive Learning Agent (Phase 7) for lessons it inserted.
    is_revision: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    module: Mapped["Module"] = relationship(back_populates="lessons")
