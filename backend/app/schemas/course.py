"""
Pydantic schemas for course creation and responses.
"""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import CourseStatus, LearningStyle, SkillLevel

_LEVEL_ORDER = {SkillLevel.beginner: 0, SkillLevel.intermediate: 1, SkillLevel.advanced: 2}


class CourseCreate(BaseModel):
    topic: str = Field(min_length=2, max_length=255, examples=["Python for Data Science"])
    current_level: SkillLevel
    target_level: SkillLevel
    study_minutes_per_day: int = Field(gt=0, le=960, description="Minutes of study per day")
    target_completion_date: date
    preferred_learning_style: LearningStyle

    @field_validator("target_completion_date")
    @classmethod
    def must_be_future(cls, value: date) -> date:
        if value <= date.today():
            raise ValueError("target_completion_date must be in the future")
        return value

    @model_validator(mode="after")
    def target_must_be_ahead_of_current(self) -> "CourseCreate":
        if _LEVEL_ORDER[self.target_level] <= _LEVEL_ORDER[self.current_level]:
            raise ValueError("target_level must be higher than current_level")
        return self


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic: str
    current_level: SkillLevel
    target_level: SkillLevel
    study_minutes_per_day: int
    target_completion_date: date
    preferred_learning_style: LearningStyle
    status: CourseStatus
    created_at: datetime
    updated_at: datetime
