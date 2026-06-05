import re
from schemas.agent_state_schema import WorkflowState


_REQUIRED_RESOURCE_KEYS = {"theory_note", "dataset_instruction", "practice_guide", "graded_quiz", "learning_path", "citations"}
_FORBIDDEN_PATTERNS = {"fit_transform\\(X_test": "不能对测试集使用 fit_transform", "fit_transform\\(data\\.data": "不能对整个数据集先进行 fit_transform"}


def _hard_rule_review(state: WorkflowState) -> list[str]:
    issues = []
    resources = state.generated_resources or {}

    for key in _REQUIRED_RESOURCE_KEYS:
        val = resources.get(key)
        if not val:
            issues.append(f"缺少必须的模块：{key}")
        elif isinstance(val, list) and len(val) == 0:
            issues.append(f"模块内容为空：{key}")
        elif isinstance(val, str) and len(val.strip()) < 10:
            issues.append(f"模块内容过短：{key}")

    quiz = resources.get("graded_quiz")
    if isinstance(quiz, list) and len(quiz) < 3:
        issues.append("测验题目数量不足，最少需要3道")

    code_str = str(resources.get("practice_guide", ""))
    for pattern, reason in _FORBIDDEN_PATTERNS.items():
        if re.search(pattern, code_str):
            issues.append(f"代码存在安全隐患或不良实践：{reason}")
            
    return issues


def _llm_review(resources: dict, evidence_titles: list[str]) -> tuple[bool, list[str], str]:
    import json
    from agents.llm_service import call_llm_json
    
    resources_summary = {
        "theory_note_preview": resources.get("theory_note", "")[:500],
        "quiz_count": len(resources.get("graded_quiz", [])),
        "code_preview": str(resources.get("practice_guide", []))[:500],
        "citations": resources.get("citations", [])
    }
    
    system_prompt = '''你是一个严格的教育内容审核专家。
请检查提供的教学资源是否结构完整、逻辑连贯、难度匹配，并且引用的知识库证据真实有效。
JSON 格式要求如下：
{
  "passed": true|false,
  "issues": ["问题1"], // 如果 passed 为 true，这里应该为空数组
  "summary": "审核通过..."
}'''

    data = call_llm_json(system_prompt, f"知识库证据：{evidence_titles}\n生成资源：\n{json.dumps(resources_summary, ensure_ascii=False)}")
    return data.get("passed", False), data.get("issues", []), data.get("summary", "LLM审核完成")


def run_reviewer_agent(state: WorkflowState) -> WorkflowState:
    import logging
    logger = logging.getLogger(__name__)
    
    resources = state.generated_resources or {}
    evidence_titles = [item.title for item in state.retrieved_knowledge]
    
    # 1. 代码层硬规则检查
    hard_issues = _hard_rule_review(state)
    
    # 2. LLM 检查
    llm_issues = []
    llm_summary = "LLM 审核完成"
    agent_status = "fallback"
    
    try:
        llm_passed, llm_issues, llm_summary = _llm_review(resources, evidence_titles)
        agent_status = "llm"
    except Exception as e:
        logger.warning(f"LLM 审核失败 ({e})")
        
    all_issues = hard_issues + llm_issues
    
    if all_issues:
        state.review_passed = False
        state.reviewer_feedback = "；".join(all_issues)
        status = "failed"
        summary = state.reviewer_feedback
    else:
        state.review_passed = True
        state.reviewer_feedback = llm_summary if agent_status == "llm" else "规则审核通过"
        status = "completed"
        summary = state.reviewer_feedback

    state.agent_events.append({
        "agent": "审核纠偏 Agent",
        "status": status,
        "engine": agent_status,
        "summary": f"[{'LLM 审核' if agent_status == 'llm' else '规则降级'}] {summary}",
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
            break
    else:
        steps.append({"agent": agent, "status": status, "summary": summary})
    
    trace["steps"] = steps
    resources["agent_trace"] = trace
