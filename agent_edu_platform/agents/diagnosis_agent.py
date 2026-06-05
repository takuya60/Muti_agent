from schemas.agent_state_schema import DiagnosisResult, WorkflowState


_SCORE_THRESHOLDS = {
    "python": (60, "Python 编程基础"),
    "linear_algebra": (65, "线性代数与矩阵理解"),
    "ml_basic": (65, "机器学习基本概念"),
    "model_evaluation": (70, "模型评估指标"),
}

_LEVEL_LABELS = {
    "python_level": {
        "none": "Python 基础薄弱",
        "basic": "具备 Python 基础语法",
        "data_basic": "具备 NumPy/Pandas 基础",
        "script": "能独立写数据处理脚本",
    },
    "math_level": {
        "fear_formula": "数学公式接受度较低",
        "basic": "具备基础函数和概率直觉",
        "college_math": "学过线性代数或概率论",
        "derivation": "能接受较完整公式推导",
    },
    "ml_level": {
        "none": "机器学习零基础",
        "concept": "看过机器学习概念",
        "sklearn_demo": "跑过 sklearn 示例",
        "project": "做过简单机器学习项目",
    },
}


_INITIAL_WEAK_POINTS = {
    "python_level": {
        "none": ["Python 基础语法", "NumPy/Pandas 数据处理"],
        "basic": ["NumPy/Pandas 数据处理"],
        "data_basic": [],
        "script": [],
    },
    "math_level": {
        "fear_formula": ["函数直觉与概率基础"],
        "basic": [],
        "college_math": [],
        "derivation": [],
    },
    "ml_level": {
        "none": ["机器学习任务理解", "训练集/测试集划分"],
        "concept": ["sklearn 标准建模流程"],
        "sklearn_demo": [],
        "project": [],
    },
}


def _fallback_diagnosis(state: WorkflowState) -> DiagnosisResult:
    profile = state.learner_profile
    scores = profile.get("test_scores", {})
    weak_points = list(profile.get("weak_points", []))
    strengths: list[str] = []

    for field, options in _INITIAL_WEAK_POINTS.items():
        for point in options.get(profile.get(field, ""), []):
            if point not in weak_points:
                weak_points.append(point)

    for field, labels in _LEVEL_LABELS.items():
        label = labels.get(profile.get(field, ""))
        if label:
            strengths.append(label)

    for key, (threshold, label) in _SCORE_THRESHOLDS.items():
        score = int(scores.get(key, 0))
        if score < threshold and label not in weak_points:
            weak_points.append(label)
        elif score >= 80 and label not in strengths:
            strengths.append(label)

    python_level = profile.get("python_level", "basic")
    math_level = profile.get("math_level", "basic")
    ml_level = profile.get("ml_level", "none")
    practice_preference = profile.get("practice_preference", "balanced")
    theory_preference = profile.get("theory_preference", "intuitive")

    if python_level == "script" and math_level in {"college_math", "derivation"} and ml_level in {"sklearn_demo", "project"}:
        recommended_level = "advanced"
    elif python_level in {"data_basic", "script"} and ml_level in {"concept", "sklearn_demo", "project"}:
        recommended_level = "intermediate"
    elif python_level == "none" or ml_level == "none":
        recommended_level = "beginner_plus"
    else:
        recommended_level = "beginner_plus"

    strategy_parts: list[str] = []
    if python_level == "none":
        strategy_parts.append("先补 Python 与数据处理基础")
    if math_level == "fear_formula" or theory_preference == "low_formula":
        strategy_parts.append("少用公式，多用直觉、类比和案例")
    elif theory_preference == "derivation":
        strategy_parts.append("保留关键公式和必要推导")
    if practice_preference == "project_first":
        strategy_parts.append("先给任务场景和代码步骤，再回到原理解释")
    elif practice_preference == "theory_first":
        strategy_parts.append("先建立概念框架，再安排代码练习")

    strategy = "；".join(strategy_parts) or "用案例和图解降低理解门槛"

    return DiagnosisResult(
        weak_points=weak_points,
        strengths=strengths,
        recommended_level=recommended_level,
        learning_objectives=[
            "明确当前机器学习学习起点和下一步路径",
            "完成本关讲义、代码练习与测验闭环",
            "形成可进入下一关或切换分支的学习依据",
        ],
        explanation_strategy=strategy,
    )

def _llm_diagnosis(state: WorkflowState) -> DiagnosisResult:
    import json
    from agents.llm_service import call_llm_json
    
    profile_json = json.dumps(state.learner_profile, ensure_ascii=False)
    system_prompt = '''你是一个专业的机器学习教育学情诊断专家。
请根据用户的画像数据，深度分析用户的学习状态。
你需要输出一个严格合法的 JSON 对象，格式要求如下：
{
  "weak_points": ["薄弱点1", "薄弱点2"],
  "strengths": ["优势1", "优势2"],
  "recommended_level": "beginner|beginner_plus|intermediate|advanced",
  "learning_objectives": ["目标1", "目标2", "目标3"],
  "explanation_strategy": "..."
}'''
    
    data = call_llm_json(system_prompt, f"用户画像数据：\n{profile_json}")
    
    level = data.get("recommended_level", "beginner_plus")
    if level not in ["beginner", "beginner_plus", "intermediate", "advanced"]:
        level = "beginner_plus"
        
    return DiagnosisResult(
        weak_points=data.get("weak_points", []),
        strengths=data.get("strengths", []),
        recommended_level=level,
        learning_objectives=data.get("learning_objectives", ["明确当前学习起点和下一步路径"]),
        explanation_strategy=data.get("explanation_strategy", "用案例和图解降低理解门槛"),
    )

def run_diagnosis_agent(state: WorkflowState) -> WorkflowState:
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        diagnosis = _llm_diagnosis(state)
        agent_status = "llm_completed"
        logger.info(f"LLM 画像诊断成功，推荐难度：{diagnosis.recommended_level}")
    except Exception as e:
        logger.warning(f"LLM 画像诊断失败 ({type(e).__name__}: {e})，降级为规则诊断")
        diagnosis = _fallback_diagnosis(state)
        agent_status = "fallback_completed"
        
    state.diagnosis = diagnosis
    state.agent_events.append({
        "agent": "画像诊断 Agent",
        "status": "completed",
        "engine": "llm" if agent_status == "llm_completed" else "fallback",
        "summary": f"[{'LLM 诊断' if agent_status == 'llm_completed' else '规则降级'}] 识别出 {len(diagnosis.weak_points)} 个薄弱点，策略：{diagnosis.explanation_strategy}",
    })
    return state
