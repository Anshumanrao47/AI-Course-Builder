"""
Shared enums used across models and schemas.

Kept as plain Python (str) enums so they serialize cleanly to JSON and map
directly to Postgres ENUM types via SQLAlchemy.
"""
import enum


class SkillLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class LearningStyle(str, enum.Enum):
    visual = "visual"           # diagrams, videos, illustrated examples
    reading_writing = "reading_writing"  # text explanations, notes
    hands_on = "hands_on"       # exercises and projects first
    mixed = "mixed"


class CourseStatus(str, enum.Enum):
    pending_assessment = "pending_assessment"  # created, skill assessment not done yet (Phase 3)
    assessing = "assessing"
    active = "active"           # roadmap generated and in progress (Phase 4+)
    completed = "completed"
    archived = "archived"


class ModuleStatus(str, enum.Enum):
    locked = "locked"
    unlocked = "unlocked"
    completed = "completed"


class LessonStatus(str, enum.Enum):
    locked = "locked"
    unlocked = "unlocked"
    completed = "completed"


class QuestionType(str, enum.Enum):
    multiple_choice = "multiple_choice"
    coding = "coding"
    descriptive = "descriptive"


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
