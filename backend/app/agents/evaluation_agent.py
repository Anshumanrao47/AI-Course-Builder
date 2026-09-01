"""
Agent 5: Evaluation Agent.

Grades a quiz attempt. Multiple-choice questions are graded deterministically
(exact match against the stored correct_answer); the agent's job is to turn
that raw grading into weak-topic detection and a human-readable
recommendation, since that requires judgment a simple string match doesn't
capture (e.g. noticing a cluster of misses in one subtopic).
"""
from app.core.ai_client import call_structured
from app.agents.ai_schemas import QuizEvaluation


def evaluate_quiz(
    *,
    module_title: str,
    graded: list[dict],  # [{question, topic, is_correct}]
) -> QuizEvaluation:
    correct = sum(1 for g in graded if g["is_correct"])
    score = round(100 * correct / len(graded), 1) if graded else 0.0

    return call_structured(
        system_prompt=(
            "You are the Evaluation Agent. Given per-question grading results "
            "for one quiz, identify which specific topics the learner is weak "
            "in and write one short, actionable recommendation sentence. Use "
            "the provided score as-is — do not recalculate it."
        ),
        user_prompt=f"Module: {module_title}\nScore: {score}\nGraded questions: {graded}",
        response_model=QuizEvaluation,
        mock_fn=lambda: _mock_evaluation(module_title, graded, score),
    )


def _mock_evaluation(module_title: str, graded: list[dict], score: float) -> QuizEvaluation:
    weak_topics = list(dict.fromkeys(g["topic"] for g in graded if not g["is_correct"]))[:5]

    if score >= 85:
        recommendation = f"Strong grasp of {module_title} — ready to move on."
    elif score >= 60:
        recommendation = (
            f"Solid overall, but review {', '.join(weak_topics) or 'the missed questions'} "
            "before moving on."
        )
    else:
        recommendation = (
            f"Revisit {', '.join(weak_topics) or module_title} before continuing — "
            "we'll add a few extra practice lessons."
        )

    return QuizEvaluation(score=score, weak_topics=weak_topics, recommendation=recommendation)
