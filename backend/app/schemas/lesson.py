"""
Pydantic schemas for lessons.
"""
import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import LessonStatus


class LessonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    estimated_minutes: int
    status: LessonStatus
    is_revision: bool
    objectives: list[str] | None
    explanation: str | None
    examples: list[str] | None
    exercise: str | None
    summary: str | None


class LessonCompleteResponse(BaseModel):
    lesson: LessonRead
    module_completed: bool
    quiz_id: uuid.UUID | None = None
    next_lesson_id: uuid.UUID | None = None
