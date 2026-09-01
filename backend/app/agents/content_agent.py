"""
Agent 3: Content Generation Agent.

Generates a single lesson's full content, adapted to the learner's level
and preferred learning style. Called lazily the first time a lesson is
opened (see api/lessons.py), not upfront for the whole roadmap.
"""
from app.core.ai_client import call_structured
from app.agents.ai_schemas import LessonContentOut
from app.models.enums import LearningStyle, SkillLevel


def generate_lesson_content(
    *,
    course_topic: str,
    module_title: str,
    lesson_title: str,
    skill_level: SkillLevel,
    learning_style: LearningStyle,
) -> LessonContentOut:
    style_hint = {
        LearningStyle.visual: "Lean on described diagrams/visual mental models and illustrated examples.",
        LearningStyle.reading_writing: "Lean on clear written explanations and structured notes.",
        LearningStyle.hands_on: "Lean on a practical, exercise-first framing — get the learner typing/doing quickly.",
        LearningStyle.mixed: "Blend explanation, a visual analogy, and a hands-on exercise.",
    }[learning_style]

    return call_structured(
        system_prompt=(
            "You are the Content Generation Agent. Write one self-contained "
            "lesson: clear learning objectives, a simple-language explanation, "
            "concrete examples, one practical exercise, and a short summary. "
            f"{style_hint}"
        ),
        user_prompt=(
            f"Course topic: {course_topic}\n"
            f"Module: {module_title}\n"
            f"Lesson: {lesson_title}\n"
            f"Learner's current skill level: {skill_level.value}\n"
            "Keep the explanation appropriately paced for that level — don't "
            "over-explain for advanced learners or skip basics for beginners."
        ),
        response_model=LessonContentOut,
        mock_fn=lambda: _mock_content(module_title, lesson_title, skill_level),
    )


def _mock_content(module_title: str, lesson_title: str, skill_level: SkillLevel) -> LessonContentOut:
    return LessonContentOut(
        objectives=[
            f"Understand what '{lesson_title}' means in the context of {module_title}",
            "Apply the idea in a small example",
        ],
        explanation=(
            f"This lesson covers {lesson_title.lower()}, part of {module_title}. "
            f"At a {skill_level.value} level, focus on building an accurate mental "
            "model before optimizing for speed or edge cases. Start from a concrete "
            "example, then generalize the pattern."
        ),
        examples=[
            f"Example 1: a minimal case showing {lesson_title.lower()} in isolation.",
            f"Example 2: {lesson_title.lower()} combined with something you already know.",
        ],
        exercise=(
            f"Try it yourself: write a small example that uses {lesson_title.lower()}, "
            "then explain out loud (or in comments) why each line is there."
        ),
        summary=f"You've covered the core idea behind {lesson_title.lower()} and practiced applying it.",
    )
