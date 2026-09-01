"""
Agent 4: Quiz Generation Agent.

Generates a module's quiz from its lessons' content, adjusting overall
difficulty based on the learner's most recent quiz performance (if any).
"""
from app.core.ai_client import call_structured
from app.agents.ai_schemas import QuizQuestionSet, QuizQuestionOut
from app.models.enums import Difficulty, QuestionType


def generate_quiz(
    *,
    module_title: str,
    lesson_summaries: list[str],
    recent_avg_score: float | None,
) -> QuizQuestionSet:
    if recent_avg_score is None:
        difficulty_hint = "Use a mix of easy and medium questions — this is the learner's first quiz."
    elif recent_avg_score >= 85:
        difficulty_hint = "The learner has been scoring well; lean toward medium/hard questions."
    elif recent_avg_score < 60:
        difficulty_hint = "The learner has been struggling; lean toward easy/medium questions."
    else:
        difficulty_hint = "Use a balanced mix of easy, medium, and hard questions."

    return call_structured(
        system_prompt=(
            "You are the Quiz Generation Agent. Write quiz questions based "
            "strictly on the given lesson summaries for one module. Prefer "
            "multiple_choice; use 'descriptive' only for a question that "
            "genuinely needs a short written answer. Tag each question with the "
            "specific subtopic it tests so weak areas can be identified later."
        ),
        user_prompt=(
            f"Module: {module_title}\n"
            f"Lesson summaries covered: {lesson_summaries}\n"
            f"{difficulty_hint}\n"
            "Generate 5 questions."
        ),
        response_model=QuizQuestionSet,
        mock_fn=lambda: _mock_quiz(module_title, lesson_summaries, recent_avg_score),
    )


def _mock_quiz(module_title: str, lesson_summaries: list[str], recent_avg_score: float | None) -> QuizQuestionSet:
    difficulty = Difficulty.medium
    if recent_avg_score is not None:
        difficulty = Difficulty.hard if recent_avg_score >= 85 else (
            Difficulty.easy if recent_avg_score < 60 else Difficulty.medium
        )

    num_questions = max(len(lesson_summaries), 1)
    questions = [
        QuizQuestionOut(
            question=f"[{module_title}] Which of the following best applies to concept {i + 1}?",
            question_type=QuestionType.multiple_choice,
            options=["Correct concept", "Common misconception A", "Common misconception B", "Unrelated concept"],
            correct_answer="Correct concept",
            topic=f"{module_title} — concept {i + 1}",
            difficulty=difficulty,
        )
        for i in range(min(num_questions, 5))
    ]
    return QuizQuestionSet(questions=questions)
