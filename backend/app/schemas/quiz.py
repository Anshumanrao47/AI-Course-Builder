"""
Pydantic schemas for quizzes. QuizQuestionPublic deliberately omits
correct_answer — it's stripped before ever reaching the client.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Difficulty, QuestionType


class QuizQuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question: str
    question_type: QuestionType
    options: list[str] | None
    difficulty: Difficulty


class QuizRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    questions: list[QuizQuestionPublic]


class QuizAnswerIn(BaseModel):
    question_id: uuid.UUID
    answer: str


class QuizSubmitRequest(BaseModel):
    answers: list[QuizAnswerIn]


class QuizAttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    score: float
    weak_topics: list[str]
    recommendation: str
    submitted_at: datetime
    next_action: str
    adaptive_message: str
