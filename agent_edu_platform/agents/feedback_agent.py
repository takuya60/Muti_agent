from schemas.agent_state_schema import WorkflowState


def run_feedback_agent(state: WorkflowState, quiz_accuracy: float | None = None, learner_feedback: str = "") -> WorkflowState:
    if quiz_accuracy is None:
        action = "保持当前路径，并在完成实操后进入测试题"
        resource_type = "standard_practice"
    elif quiz_accuracy < 0.6 or "太难" in learner_feedback:
        action = "生成降维解释，补充前置知识和更细步骤"
        resource_type = "remedial_explanation"
    elif quiz_accuracy > 0.85 or "太简单" in learner_feedback:
        action = "生成进阶挑战任务和参数调优练习"
        resource_type = "advanced_challenge"
    else:
        action = "生成同难度变式练习，巩固薄弱知识点"
        resource_type = "reinforcement"

    state.feedback_decision = {
        "quiz_accuracy": quiz_accuracy,
        "learner_feedback": learner_feedback,
        "next_action": action,
        "resource_type": resource_type,
    }
    state.agent_events.append({
        "agent": "反馈决策 Agent",
        "status": "completed",
        "summary": action,
    })
    return state
