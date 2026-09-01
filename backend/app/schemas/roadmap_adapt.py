"""
Pydantic schema for the manual /roadmap/adapt endpoint.
"""
import uuid

from pydantic import BaseModel


class RoadmapAdaptRequest(BaseModel):
    course_id: uuid.UUID


class RoadmapAdaptResponse(BaseModel):
    next_action: str
    message: str
    based_on_module: str
    based_on_score: float
