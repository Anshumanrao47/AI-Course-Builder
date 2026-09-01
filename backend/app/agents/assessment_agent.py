"""
Agent 1: Skill Assessment Agent.

Generates assessment questions for a topic/level, and evaluates the
user's answers into a skill level + strengths/weaknesses.
"""
from app.core.ai_client import call_structured
from app.agents.ai_schemas import AssessmentQuestionSet, AssessmentQuestionOut, AssessmentResult
from app.models.enums import SkillLevel


def generate_assessment_questions(topic: str, current_level: SkillLevel) -> AssessmentQuestionSet:
    return call_structured(
        system_prompt=(
            "You are the Skill Assessment Agent in an AI course builder. "
            "Generate multiple-choice questions that accurately probe whether a "
            "learner is at the level they claim, covering a spread of subtopics "
            "within the given topic."
        ),
        user_prompt=(
            f"Topic: {topic}\n"
            f"Learner's self-reported level: {current_level.value}\n"
            "Generate 5 multiple-choice questions, each with exactly 4 options "
            "and one correct_answer that matches one option exactly. Vary the "
            "subtopics covered."
        ),
        response_model=AssessmentQuestionSet,
        mock_fn=lambda: _mock_questions(topic, current_level),
    )


def evaluate_assessment(
    topic: str, current_level: SkillLevel, answered: list[dict]
) -> AssessmentResult:
    """
    `answered` is a list of {question, topic, options, correct_answer, selected_answer}.
    """
    correct_count = sum(1 for a in answered if a["selected_answer"] == a["correct_answer"])
    accuracy = correct_count / len(answered) if answered else 0

    return call_structured(
        system_prompt=(
            "You are the Skill Assessment Agent. Given a learner's answers to a "
            "diagnostic quiz, determine their real skill level and identify "
            "specific strengths and weaknesses by subtopic (not just 'good' or "
            "'bad' — name the concepts)."
        ),
        user_prompt=(
            f"Topic: {topic}\n"
            f"Self-reported level: {current_level.value}\n"
            f"Accuracy: {correct_count}/{len(answered)} ({accuracy:.0%})\n"
            f"Answers: {answered}"
        ),
        response_model=AssessmentResult,
        mock_fn=lambda: _mock_result(current_level, accuracy, answered),
    )


# --- Mocks (used when USE_MOCK_AI=true or no API key is configured) --------

def _mock_questions(topic: str, current_level: SkillLevel) -> AssessmentQuestionSet:
    subtopics = ["Fundamentals", "Core Syntax", "Data Structures", "Control Flow", "Best Practices"]
    questions = [
        AssessmentQuestionOut(
            question=f"[{topic}] Which statement best describes {sub.lower()} at a "
                      f"{current_level.value} level?",
            options=["Option A", "Option B (correct)", "Option C", "Option D"],
            correct_answer="Option B (correct)",
            topic=sub,
        )
        for sub in subtopics
    ]
    return AssessmentQuestionSet(questions=questions)


def _mock_result(current_level: SkillLevel, accuracy: float, answered: list[dict]) -> AssessmentResult:
    levels = list(SkillLevel)
    idx = levels.index(current_level)
    if accuracy >= 0.8 and idx < len(levels) - 1:
        skill_level = levels[idx + 1]
    elif accuracy < 0.4 and idx > 0:
        skill_level = levels[idx - 1]
    else:
        skill_level = current_level

    topics = [a.get("topic", "General") for a in answered]
    correct_topics = [a.get("topic", "General") for a in answered if a["selected_answer"] == a["correct_answer"]]
    incorrect_topics = [t for t in topics if t not in correct_topics] or ["Fundamentals"]

    return AssessmentResult(
        skill_level=skill_level,
        strengths=list(dict.fromkeys(correct_topics))[:5] or ["Getting started"],
        weaknesses=list(dict.fromkeys(incorrect_topics))[:5],
    )
