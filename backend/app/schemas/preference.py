"""
Pydantic schemas for account-level learning preferences.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import LearningStyle


class PreferenceUpdate(BaseModel):
    default_learning_style: LearningStyle | None = None
    default_study_minutes_per_day: int | None = Field(default=None, gt=0, le=960)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)


class PreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    default_learning_style: LearningStyle
    default_study_minutes_per_day: int
    timezone: str
    created_at: datetime
    updated_at: datetime
