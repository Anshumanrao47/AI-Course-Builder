"""
UserLearningPreference model.

Reusable, account-level defaults (as opposed to the per-course choices
captured on Course, e.g. a course's own study time / style can still
override these). One row per user.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, ForeignKey, String, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import LearningStyle


class UserLearningPreference(Base):
    __tablename__ = "user_learning_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    default_learning_style: Mapped[LearningStyle] = mapped_column(
        SAEnum(LearningStyle, name="learning_style"),
        nullable=False,
        default=LearningStyle.mixed,
    )
    default_study_minutes_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="preference")  # noqa: F821
