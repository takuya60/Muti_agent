from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.diagnosis_agent import run_diagnosis_agent
from agents.feedback_agent import run_feedback_agent
from agents.generator_agent import run_generator_agent
from agents.graph_state import AgentGraphState
from agents.retrieval_agent import run_retrieval_agent
from agents.reviewer_agent import run_reviewer_agent
from agents.state import from_workflow_state, to_workflow_state
from evaluation.metrics import evaluate_resources

# 最大重试次数
MAX_RETRY = 2

# 节点的定义
def diagnosis_node(state: AgentGraphState) -> AgentGraphState:
    workflow_state = run_diagnosis_agent(to_workflow_state(state))
    return from_workflow_state(workflow_state)


def retrieval_node(state: AgentGraphState) -> AgentGraphState:
    workflow_state = run_retrieval_agent(to_workflow_state(state))
    return from_workflow_state(workflow_state)


def generation_node(state: AgentGraphState) -> AgentGraphState:
    workflow_state = run_generator_agent(to_workflow_state(state))
    return from_workflow_state(workflow_state)


def review_node(state: AgentGraphState) -> AgentGraphState:
    workflow_state = run_reviewer_agent(to_workflow_state(state))
    if not workflow_state.review_passed:
        workflow_state.retry_count += 1
    return from_workflow_state(workflow_state)


def feedback_node(state: AgentGraphState) -> AgentGraphState:
    workflow_state = run_feedback_agent(
        to_workflow_state(state),
        quiz_accuracy=state.get("quiz_accuracy"),
        learner_feedback=state.get("learner_feedback", ""),
    )
    return from_workflow_state(workflow_state)


def evaluate_node(state: AgentGraphState) -> AgentGraphState:
    workflow_state = to_workflow_state(state)
    workflow_state.evaluation = evaluate_resources(workflow_state).model_dump()
    workflow_state.agent_events.append({
        "agent": "评测模块",
        "status": "completed",
        "summary": "完成幻觉风险、难度适配和知识覆盖率估算",
    })
    return from_workflow_state(workflow_state)


def route_after_review(state: AgentGraphState) -> str:
    if state.get("review_passed"):
        return "feedback"
    if state.get("retry_count", 0) >= MAX_RETRY:
        return "feedback"
    return "generation"


def build_graph():
    builder = StateGraph(AgentGraphState)

    builder.add_node("diagnosis", diagnosis_node)
    builder.add_node("retrieval", retrieval_node)
    builder.add_node("generation", generation_node)
    builder.add_node("review", review_node)
    builder.add_node("feedback", feedback_node)
    builder.add_node("evaluate", evaluate_node)

    builder.add_edge(START, "diagnosis")
    builder.add_edge("diagnosis", "retrieval")
    builder.add_edge("retrieval", "generation")
    builder.add_edge("generation", "review")
    builder.add_conditional_edges(
        "review",
        route_after_review,
        {
            "generation": "generation",
            "feedback": "feedback",
        },
    )
    builder.add_edge("feedback", "evaluate")
    builder.add_edge("evaluate", END)

    return builder.compile()
