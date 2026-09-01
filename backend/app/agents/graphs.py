"""
LangGraph orchestration.

Two small, linear graphs chain agents that always run back-to-back as a
result of a single user action:

  planning_graph:  evaluate_assessment -> plan_roadmap
    Triggered by POST /assessment/submit. The learner has just answered
    the diagnostic quiz; there's no further human input needed before the
    roadmap can be generated, so both agents run in one graph invocation.

  adaptive_graph:   evaluate_quiz -> adapt_roadmap
    Triggered by POST /quizzes/{id}/submit. Same reasoning: grading and
    deciding how to adapt the roadmap are two agent calls with no user
    interaction in between.

Content generation (per-lesson) and quiz generation (per-module) are each
a single agent call triggered by a GET request the first time that
resource is opened, so they're invoked directly from the API layer
(app/api/lessons.py, app/api/quizzes.py) rather than wrapped in a graph —
a one-node graph would add indirection without adding orchestration value.
"""
from langgraph.graph import StateGraph, END

from app.agents.state import CourseState
from app.agents.assessment_agent import evaluate_assessment
from app.agents.planner_agent import generate_roadmap
from app.agents.evaluation_agent import evaluate_quiz
from app.agents.adaptive_agent import adapt_roadmap
from app.models.enums import LearningStyle, SkillLevel


# --- Planning graph: skill assessment -> course roadmap ---------------------

def _evaluate_assessment_node(state: CourseState) -> dict:
    result = evaluate_assessment(
        topic=state["learning_goal"],
        current_level=SkillLevel(state["current_skill_level"]),
        answered=state["assessment_answers"],
    )
    return {
        "assessment_results": result.model_dump(mode="json"),
        "strengths": result.strengths,
        "weaknesses": result.weaknesses,
    }


def _plan_roadmap_node(state: CourseState) -> dict:
    roadmap = generate_roadmap(
        topic=state["learning_goal"],
        current_level=SkillLevel(state["assessment_results"]["skill_level"]),
        target_level=SkillLevel(state["target_skill_level"]),
        strengths=state["strengths"],
        weaknesses=state["weaknesses"],
        study_minutes_per_day=state["study_minutes_per_day"],
        days_available=state.get("days_available", 60),
        learning_style=LearningStyle(state["preferred_learning_style"]),
    )
    return {"course_roadmap": [m.model_dump(mode="json") for m in roadmap.modules]}


def build_planning_graph():
    graph = StateGraph(CourseState)
    graph.add_node("evaluate_assessment", _evaluate_assessment_node)
    graph.add_node("plan_roadmap", _plan_roadmap_node)
    graph.set_entry_point("evaluate_assessment")
    graph.add_edge("evaluate_assessment", "plan_roadmap")
    graph.add_edge("plan_roadmap", END)
    return graph.compile()


_planning_graph = build_planning_graph()


def run_planning_graph(initial_state: CourseState) -> CourseState:
    return _planning_graph.invoke(initial_state)


# --- Adaptive graph: evaluate quiz -> adapt roadmap -------------------------

def _evaluate_quiz_node(state: CourseState) -> dict:
    evaluation = evaluate_quiz(module_title=state["current_module"], graded=state["_graded"])
    return {
        "quiz_scores": state.get("quiz_scores", []) + [evaluation.score],
        "weak_topics": evaluation.weak_topics,
        "recommendations": state.get("recommendations", []) + [evaluation.recommendation],
        "_evaluation": evaluation.model_dump(mode="json"),
    }


def _adapt_roadmap_node(state: CourseState) -> dict:
    evaluation = state["_evaluation"]
    plan = adapt_roadmap(
        module_title=state["current_module"],
        next_module_title=state.get("_next_module_title"),
        score=evaluation["score"],
        weak_topics=evaluation["weak_topics"],
    )
    return {
        "next_action": plan.next_action,
        "roadmap_adjustments": [a.model_dump(mode="json") for a in plan.adjustments],
        "_adaptive_message": plan.message,
    }


def build_adaptive_graph():
    graph = StateGraph(CourseState)
    graph.add_node("evaluate_quiz", _evaluate_quiz_node)
    graph.add_node("adapt_roadmap", _adapt_roadmap_node)
    graph.set_entry_point("evaluate_quiz")
    graph.add_edge("evaluate_quiz", "adapt_roadmap")
    graph.add_edge("adapt_roadmap", END)
    return graph.compile()


_adaptive_graph = build_adaptive_graph()


def run_adaptive_graph(initial_state: CourseState) -> CourseState:
    return _adaptive_graph.invoke(initial_state)
