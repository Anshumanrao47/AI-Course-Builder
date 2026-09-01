"""
Agent 6: Adaptive Learning Agent.

Reads an evaluation result and decides how the roadmap should change:
below 60% adds revision, above 85% allows fast-tracking, otherwise the
learner just advances normally. The actual DB writes (inserting a lesson,
flagging a module) happen in api/quizzes.py / services — this agent only
decides the plan.
"""
from app.core.ai_client import call_structured
from app.agents.ai_schemas import AdaptivePlan, RoadmapAdjustment


def adapt_roadmap(
    *,
    module_title: str,
    next_module_title: str | None,
    score: float,
    weak_topics: list[str],
) -> AdaptivePlan:
    return call_structured(
        system_prompt=(
            "You are the Adaptive Learning Agent. Decide, from one quiz score "
            "and its weak topics, how the roadmap should change: "
            "'revise' (score < 60 — add revision lessons, delay advanced "
            "topics), 'fast_track' (score > 85 — allow skipping ahead, add a "
            "harder exercise), or 'advance' (60-85 — proceed normally)."
        ),
        user_prompt=(
            f"Module just completed: {module_title}\n"
            f"Next module: {next_module_title or 'none — this was the last module'}\n"
            f"Score: {score}\nWeak topics: {weak_topics}"
        ),
        response_model=AdaptivePlan,
        mock_fn=lambda: _mock_plan(module_title, next_module_title, score, weak_topics),
    )


def _mock_plan(
    module_title: str, next_module_title: str | None, score: float, weak_topics: list[str]
) -> AdaptivePlan:
    if score < 60:
        adjustments = [
            RoadmapAdjustment(
                action="add_revision_lesson",
                module_title=module_title,
                detail=f"Add a revision lesson on {topic}",
            )
            for topic in (weak_topics or [module_title])
        ]
        return AdaptivePlan(
            next_action="revise",
            adjustments=adjustments,
            message=(
                f"Scored {score}% on {module_title} — adding revision lessons on "
                f"{', '.join(weak_topics) or module_title} before continuing."
            ),
        )

    if score > 85:
        adjustments = [
            RoadmapAdjustment(
                action="skip_ahead" if next_module_title else "no_change",
                module_title=next_module_title or module_title,
                detail="Learner is ahead of pace — offering a harder exercise and the option to skip revision.",
            )
        ]
        return AdaptivePlan(
            next_action="fast_track",
            adjustments=adjustments,
            message=f"Scored {score}% on {module_title} — great work, moving faster from here.",
        )

    return AdaptivePlan(
        next_action="advance",
        adjustments=[],
        message=f"Scored {score}% on {module_title} — solid, continuing as planned.",
    )
