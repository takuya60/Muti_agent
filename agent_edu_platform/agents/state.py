from __future__ import annotations

from schemas.agent_state_schema import WorkflowState
from .graph_state import AgentGraphState

# 把 LangGraph 传来的字典，转化为 Pydantic 对象
def to_workflow_state(state: AgentGraphState) -> WorkflowState:
    return WorkflowState(**state)

# 具体的 Agent 处理完之后，把 Pydantic 对象还原成字典，交还给 LangGraph 框架
def from_workflow_state(state: WorkflowState) -> AgentGraphState:
    return state.model_dump()
