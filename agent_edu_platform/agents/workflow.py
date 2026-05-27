from agents.graph import build_graph
from agents.graph_state import AgentGraphState
from schemas.agent_state_schema import WorkflowState
from schemas.learner_schema import LearnerProfile


_GRAPH = build_graph()


def run_workflow(profile: LearnerProfile, quiz_accuracy: float | None = None, learner_feedback: str = "") -> WorkflowState:
    initial_state: AgentGraphState = {
        "learner_id": profile.learner_id,
        "learner_profile": profile.model_dump(),
        "target_algorithm": profile.target_algorithm,
        "review_passed": False,
        "retry_count": 0,
        "agent_events": [],
        "feedback_decision": None,
        "reviewer_feedback": "",
        "generated_resources": None,
        "evaluation": None,
        "quiz_accuracy": quiz_accuracy,
        "learner_feedback": learner_feedback,
    }

    result = _GRAPH.invoke(initial_state)
    return WorkflowState(**result)
