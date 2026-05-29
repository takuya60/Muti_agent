from schemas.agent_state_schema import WorkflowState


_REQUIRED_RESOURCE_KEYS = {"theory_note", "dataset_instruction", "practice_guide", "graded_quiz", "learning_path", "citations"}
_FORBIDDEN_PATTERNS = ["fit_transform(X_test", "fit_transform(data.data"]


def run_reviewer_agent(state: WorkflowState) -> WorkflowState:
    resources = state.generated_resources or {}
    issues: list[str] = []

    missing = _REQUIRED_RESOURCE_KEYS - set(resources)
    if missing:
        issues.append(f"资源结构缺少字段：{', '.join(sorted(missing))}")

    practice_guide = resources.get("practice_guide", [])
    code_text = "\n".join(step.get("python_code", "") for step in practice_guide)
    for pattern in _FORBIDDEN_PATTERNS:
        if pattern in code_text:
            issues.append(f"代码疑似存在机器学习流程错误：{pattern}")

    quiz_count = len(resources.get("graded_quiz", []))
    if quiz_count < 3:
        issues.append("分阶测试题不足 3 道")

    citations = resources.get("citations", [])
    if not citations:
        issues.append("生成内容缺少知识库引用来源")

    if not resources.get("learning_path"):
        issues.append("学习路径为空")

    if state.retrieved_knowledge and citations:
        evidence_titles = {item.title for item in state.retrieved_knowledge}
        if not any(citation in evidence_titles for citation in citations):
            issues.append("引用来源与检索证据不一致")

    if issues:
        state.review_passed = False
        state.reviewer_feedback = "；".join(issues)
        status = "failed"
        summary = state.reviewer_feedback
    else:
        state.review_passed = True
        state.reviewer_feedback = "审核通过：结构完整、无明显数据泄露模式、包含知识库引用。"
        status = "completed"
        summary = state.reviewer_feedback

    state.agent_events.append({
        "agent": "审核纠偏 Agent",
        "status": status,
        "summary": summary,
    })
    _sync_agent_trace(resources, "审核纠偏 Agent", status, summary)
    return state


def _sync_agent_trace(resources: dict, agent: str, status: str, summary: str) -> None:
    trace = resources.get("agent_trace") or {}
    steps = trace.get("steps") or []
    for step in steps:
        if step.get("agent") == agent:
            step["status"] = status
            step["summary"] = summary
            return
    steps.append({
        "agent": agent,
        "title": "检查内容质量",
        "status": status,
        "summary": summary,
        "details": ["结构完整性", "引用来源", "数据泄露风险", "难度匹配"],
    })
    trace["steps"] = steps
    resources["agent_trace"] = trace
