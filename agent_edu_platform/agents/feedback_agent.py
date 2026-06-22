from schemas.agent_state_schema import WorkflowState


def _fallback_feedback(quiz_accuracy: float | None, learner_feedback: str) -> tuple[str, str]:
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
    return action, resource_type


def _llm_feedback(quiz_accuracy: float | None, learner_feedback: str) -> tuple[str, str]:
    import json
    from agents.llm_service import call_llm_json
    system_prompt = '''你是一个学习反馈规划师。
根据学生的测验准确率和反馈，决定下一步的教学动作和资源类型。
JSON 格式要求如下：
{
  "next_action": "生成降维解释...",
  "resource_type": "standard_practice|remedial_explanation|advanced_challenge|reinforcement"
}'''
    data = call_llm_json(system_prompt, f"准确率：{quiz_accuracy}\n用户反馈：{learner_feedback}")
    
    rt = data.get("resource_type", "standard_practice")
    if rt not in ["standard_practice", "remedial_explanation", "advanced_challenge", "reinforcement"]:
        rt = "standard_practice"
        
    return data.get("next_action", "保持当前路径"), rt


def run_feedback_agent(state: WorkflowState, quiz_accuracy: float | None = None, learner_feedback: str = "") -> WorkflowState:
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        action, resource_type = _llm_feedback(quiz_accuracy, learner_feedback)
        engine = "llm"
    except Exception as e:
        logger.warning(f"LLM 反馈规划失败 ({e})")
        action, resource_type = _fallback_feedback(quiz_accuracy, learner_feedback)
        engine = "fallback"

    state.feedback_decision = {
        "quiz_accuracy": quiz_accuracy,
        "learner_feedback": learner_feedback,
        "next_action": action,
        "resource_type": resource_type,
    }
    state.agent_events.append({
        "agent": "反馈决策 Agent",
        "status": "completed",
        "engine": engine,
        "summary": f"[{'LLM 规划' if engine == 'llm' else '规则降级'}] {action}",
    })
    _sync_agent_trace(state.generated_resources or {}, action)
    return state


def _sync_agent_trace(resources: dict, action: str) -> None:
    from schemas.resource_schema import AgentTraceStep
    trace = resources.get("agent_trace") or {}
    
    # 获取或初始化 steps 列表
    if "steps" not in trace:
        trace["steps"] = []
        
    steps = trace["steps"]
    next_focus = resources.get("next_focus") or "当前阶段复盘"
    
    for i, step in enumerate(steps):
        is_match = False
        if hasattr(step, "agent") and getattr(step, "agent") == "反馈规划 Agent":
            is_match = True
        elif isinstance(step, dict) and step.get("agent") == "反馈规划 Agent":
            is_match = True
            
        if is_match:
            if hasattr(step, "status"):
                step.status = "completed"
                step.summary = action
                step.details = [f"下一关：{next_focus}"]
            else:
                step["status"] = "completed"
                step["summary"] = action
                step["details"] = [f"下一关：{next_focus}"]
            return
            
    steps.append(AgentTraceStep(
        agent="反馈规划 Agent",
        title="规划下一步",
        status="completed",
        summary=action,
        details=[f"下一关：{next_focus}"]
    ))
    
    resources["agent_trace"] = trace
