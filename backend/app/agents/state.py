"""
Shared LangGraph state for the multi-agent workflow.

Matches the fields called out in the project spec so every agent reads
and writes the same shape. Two graphs are built on top of this state (see
graphs.py): one that runs right after the skill assessment (evaluate ->
plan the roadmap), and one that runs after a quiz submission (evaluate ->
adapt the roadmap). Both stay small and synchronous because each is
triggered by a single user action rather than a long-running background
process.
"""
from typing import TypedDict


class CourseState(TypedDict, total=False):
    # Identity
    user_id: str
    course_id: str

    # Goal / preferences captured at course creation
    learning_goal: str
    current_skill_level: str
    target_skill_level: str
    preferred_learning_style: str
    study_minutes_per_day: int

    # Skill Assessment Agent output
    assessment_answers: list[dict]  # [{question, options, selected_answer, correct_answer}]
    assessment_results: dict        # {skill_level, strengths, weaknesses}
    strengths: list[str]
    weaknesses: list[str]

    # Course Planning Agent output
    course_roadmap: list[dict]      # [{title, estimated_minutes, lessons: [title, ...]}]

    # Runtime progress
    current_module: str
    completed_lessons: list[str]

    # Quiz Generation / Evaluation Agent output
    quiz_scores: list[float]
    weak_topics: list[str]
    recommendations: list[str]

    # Adaptive Learning Agent output
    next_action: str  # "advance" | "revise" | "fast_track"
    roadmap_adjustments: list[dict]

    # Internal/transient fields used only within a single graph invocation
    days_available: int
    _graded: list[dict]
    _evaluation: dict
    _next_module_title: str | None
    _adaptive_message: str
