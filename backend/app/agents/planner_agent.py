"""
Agent 2: Course Planning Agent.

Turns a topic + assessment results + pace into an ordered module/lesson
roadmap. Lesson bodies are NOT generated here — only titles and time
estimates — the Content Generation Agent fills each one in lazily.
"""
import math

from app.core.ai_client import call_structured
from app.agents.ai_schemas import CourseRoadmap, PlannedModule, PlannedLesson
from app.models.enums import LearningStyle, SkillLevel


def generate_roadmap(
    *,
    topic: str,
    current_level: SkillLevel,
    target_level: SkillLevel,
    strengths: list[str],
    weaknesses: list[str],
    study_minutes_per_day: int,
    days_available: int,
    learning_style: LearningStyle,
) -> CourseRoadmap:
    total_minutes_budget = max(study_minutes_per_day * days_available, 60)

    return call_structured(
        system_prompt=(
            "You are the Course Planning Agent. Design a personalized, "
            "logically ordered course roadmap: modules, each broken into "
            "lessons, with realistic time estimates. Front-load material that "
            "addresses the learner's weaknesses. Do not include a lesson's full "
            "content — titles and time estimates only."
        ),
        user_prompt=(
            f"Topic: {topic}\n"
            f"Current level: {current_level.value} -> Target level: {target_level.value}\n"
            f"Known strengths: {strengths or 'none identified'}\n"
            f"Known weaknesses: {weaknesses or 'none identified'}\n"
            f"Preferred learning style: {learning_style.value}\n"
            f"Total study time available: ~{total_minutes_budget} minutes "
            f"({study_minutes_per_day} min/day over {days_available} days)\n"
            "Produce 3-8 modules, each with 2-6 lessons, ending in a project or "
            "capstone-style final module."
        ),
        response_model=CourseRoadmap,
        mock_fn=lambda: _mock_roadmap(topic, weaknesses, total_minutes_budget),
    )


def _mock_roadmap(topic: str, weaknesses: list[str], total_minutes_budget: int) -> CourseRoadmap:
    outline = [
        ("Fundamentals", ["Getting set up", "Core concepts", "Your first exercise"]),
        ("Building blocks", ["Key building block A", "Key building block B", "Putting it together"]),
        ("Intermediate techniques", ["Technique 1", "Technique 2", "Common pitfalls"]),
        ("Applied practice", ["Guided project — part 1", "Guided project — part 2"]),
        ("Final project", ["Plan your project", "Build your project", "Review & next steps"]),
    ]
    # Nudge the first module's lessons toward known weaknesses, if any.
    if weaknesses:
        outline[0] = (
            f"Fundamentals (focus: {weaknesses[0]})",
            [f"Reviewing {w}" for w in weaknesses[:2]] + ["Core concepts"],
        )

    minutes_per_lesson = max(15, min(90, total_minutes_budget // (sum(len(l) for _, l in outline) or 1)))

    modules = [
        PlannedModule(
            title=title,
            estimated_minutes=minutes_per_lesson * len(lessons),
            lessons=[PlannedLesson(title=t, estimated_minutes=minutes_per_lesson) for t in lessons],
        )
        for title, lessons in outline
    ]
    return CourseRoadmap(modules=modules)
