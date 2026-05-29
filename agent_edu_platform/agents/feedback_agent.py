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
    _sync_agent_trace(state.generated_resources or {}, action)
    return state


def _sync_agent_trace(resources: dict, action: str) -> None:
    trace = resources.get("agent_trace") or {}
    steps = trace.get("steps") or []
    next_focus = resources.get("next_focus") or "当前阶段复盘"
    for step in steps:
        if step.get("agent") == "反馈规划 Agent":
            step["status"] = "completed"
            step["summary"] = action
            step["details"] = [f"下一关：{next_focus}"]
            return
    steps.append({
        "agent": "反馈规划 Agent",
        "title": "规划下一步",
        "status": "completed",
        "summary": action,
        "details": [f"下一关：{next_focus}"],
    })
    trace["steps"] = steps
    resources["agent_trace"] = trace
