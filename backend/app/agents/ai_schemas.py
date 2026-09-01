"""
Pydantic models the agents ask the AI provider to fill in. Kept separate
from app/schemas (the API-facing models) because these describe what the
LLM must return, not what the API returns to the frontend — the two
often differ (e.g. correct_answer is part of the AI schema but stripped
before a quiz question ever reaches the client).
"""
from pydantic import BaseModel, Field

from app.models.enums import Difficulty, QuestionType, SkillLevel


# --- Skill Assessment Agent -------------------------------------------------

class AssessmentQuestionOut(BaseModel):
    question: str
    options: list[str] = Field(min_length=2, max_length=6)
    correct_answer: str
    topic: str


class AssessmentQuestionSet(BaseModel):
    questions: list[AssessmentQuestionOut] = Field(min_length=3, max_length=10)


class AssessmentResult(BaseModel):
    skill_level: SkillLevel
    strengths: list[str] = Field(default_factory=list, max_length=10)
    weaknesses: list[str] = Field(default_factory=list, max_length=10)


# --- Course Planning Agent --------------------------------------------------

class PlannedLesson(BaseModel):
    title: str
    estimated_minutes: int = Field(gt=0, le=180)


class PlannedModule(BaseModel):
    title: str
    estimated_minutes: int = Field(gt=0, le=2400)
    lessons: list[PlannedLesson] = Field(min_length=1, max_length=8)


class CourseRoadmap(BaseModel):
    modules: list[PlannedModule] = Field(min_length=2, max_length=12)


# --- Content Generation Agent -----------------------------------------------

class LessonContentOut(BaseModel):
    objectives: list[str] = Field(min_length=1, max_length=6)
    explanation: str
    examples: list[str] = Field(min_length=1, max_length=5)
    exercise: str
    summary: str


# --- Quiz Generation Agent ---------------------------------------------------

class QuizQuestionOut(BaseModel):
    question: str
    question_type: QuestionType
    options: list[str] | None = Field(default=None, max_length=6)
    correct_answer: str
    topic: str
    difficulty: Difficulty


class QuizQuestionSet(BaseModel):
    questions: list[QuizQuestionOut] = Field(min_length=3, max_length=10)


# --- Evaluation Agent --------------------------------------------------------

class GradedAnswer(BaseModel):
    question_id: str
    is_correct: bool
    topic: str


class QuizEvaluation(BaseModel):
    score: float = Field(ge=0, le=100)
    weak_topics: list[str] = Field(default_factory=list, max_length=10)
    recommendation: str


# --- Adaptive Learning Agent --------------------------------------------------

class RoadmapAdjustment(BaseModel):
    action: str  # "add_revision_lesson" | "skip_ahead" | "increase_difficulty" | "no_change"
    module_title: str
    detail: str


class AdaptivePlan(BaseModel):
    next_action: str  # "advance" | "revise" | "fast_track"
    adjustments: list[RoadmapAdjustment] = Field(default_factory=list, max_length=10)
    message: str
