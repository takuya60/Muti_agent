from schemas.agent_state_schema import WorkflowState


def check_hallucination(state: WorkflowState) -> list[str]:
    resources = state.generated_resources or {}
    citations = resources.get("citations", [])
    if not citations:
        return ["缺少知识库引用，存在不可追溯风险"]
    return []
