"""
Pydantic schemas for reading a course's generated roadmap (modules/lessons).
"""
import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import LessonStatus, ModuleStatus


class LessonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    order_index: int
    estimated_minutes: int
    status: LessonStatus
    is_revision: bool


class ModuleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    order_index: int
    estimated_minutes: int
    status: ModuleStatus
    quiz_id: uuid.UUID | None = None
    lessons: list[LessonSummary]


class RoadmapRead(BaseModel):
    modules: list[ModuleSummary]
