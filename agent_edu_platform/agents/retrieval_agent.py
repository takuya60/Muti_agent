from rag_engine import retrieve_knowledge
from schemas.agent_state_schema import WorkflowState


def run_retrieval_agent(state: WorkflowState) -> WorkflowState:
    diagnosis_terms = " ".join(state.diagnosis.weak_points if state.diagnosis else [])
    query = f"{state.target_algorithm} {diagnosis_terms} 训练 测试 评估"
    state.retrieved_knowledge = retrieve_knowledge(query)
    state.agent_events.append({
        "agent": "知识检索 Agent",
        "status": "completed",
        "summary": f"检索到 {len(state.retrieved_knowledge)} 条知识库证据",
    })
    return state
