"""
Pydantic schemas for the skill-assessment flow.

The correct_answer for each generated question is never sent to the
client directly — it's embedded in a signed `assessment_token` (a JWT)
that the client echoes back unopened at submit time. This avoids a new
"pending assessment" DB table for what is, by design, a short-lived,
single-use exchange.
"""
import uuid

from pydantic import BaseModel, Field

from app.models.enums import SkillLevel


class AssessmentQuestionPublic(BaseModel):
    question: str
    options: list[str]


class AssessmentStartResponse(BaseModel):
    assessment_token: str
    questions: list[AssessmentQuestionPublic]


class AssessmentAnswerIn(BaseModel):
    question: str = Field(description="Must match the question text exactly as it was presented.")
    selected_answer: str


class AssessmentSubmitRequest(BaseModel):
    course_id: uuid.UUID
    assessment_token: str
    answers: list[AssessmentAnswerIn]


class AssessmentSubmitResponse(BaseModel):
    skill_level: SkillLevel
    strengths: list[str]
    weaknesses: list[str]
    modules_created: int
