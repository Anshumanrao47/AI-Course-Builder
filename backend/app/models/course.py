"""
Course model.

A Course captures what the user asked for when they started a learning
goal (topic, levels, pace, deadline, style). Modules and lessons are added
in Phase 4 once the Course Planning Agent exists to generate them.
"""
import uuid
from datetime import date, datetime

from sqlalchemy import String, DateTime, Date, Integer, ForeignKey, Enum as SAEnum, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import SkillLevel, LearningStyle, CourseStatus


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    current_level: Mapped[SkillLevel] = mapped_column(
        SAEnum(SkillLevel, name="skill_level"), nullable=False
    )
    target_level: Mapped[SkillLevel] = mapped_column(
        SAEnum(SkillLevel, name="skill_level"), nullable=False
    )
    study_minutes_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    target_completion_date: Mapped[date] = mapped_column(Date, nullable=False)
    preferred_learning_style: Mapped[LearningStyle] = mapped_column(
        SAEnum(LearningStyle, name="learning_style"), nullable=False
    )

    status: Mapped[CourseStatus] = mapped_column(
        SAEnum(CourseStatus, name="course_status"),
        nullable=False,
        default=CourseStatus.pending_assessment,
    )

    # Populated by the Skill Assessment Agent (Phase 3).
    assessed_skill_level: Mapped[SkillLevel | None] = mapped_column(
        SAEnum(SkillLevel, name="skill_level"), nullable=True
    )
    strengths: Mapped[list | None] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="courses")  # noqa: F821
    modules: Mapped[list["Module"]] = relationship(  # noqa: F821
        back_populates="course", cascade="all, delete-orphan", order_by="Module.order_index"
    )
