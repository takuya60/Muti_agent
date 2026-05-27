from schemas.agent_state_schema import DiagnosisResult, WorkflowState


_SCORE_THRESHOLDS = {
    "python": (60, "Python 编程基础"),
    "linear_algebra": (65, "线性代数与矩阵理解"),
    "ml_basic": (65, "机器学习基本概念"),
    "model_evaluation": (70, "模型评估指标"),
}


def run_diagnosis_agent(state: WorkflowState) -> WorkflowState:
    profile = state.learner_profile
    scores = profile.get("test_scores", {})
    weak_points = list(profile.get("weak_points", []))
    strengths: list[str] = []

    for key, (threshold, label) in _SCORE_THRESHOLDS.items():
        score = int(scores.get(key, 0))
        if score < threshold and label not in weak_points:
            weak_points.append(label)
        elif score >= 80:
            strengths.append(label)

    if not weak_points:
        recommended_level = "advanced"
        strategy = "以项目挑战和误差分析为主，减少基础铺垫"
    elif len(weak_points) <= 2:
        recommended_level = "intermediate"
        strategy = "保持完整实验闭环，补充关键薄弱点解释"
    else:
        recommended_level = "beginner_plus"
        strategy = "用图解类比和分步代码降低理解门槛"

    state.diagnosis = DiagnosisResult(
        weak_points=weak_points,
        strengths=strengths,
        recommended_level=recommended_level,
        learning_objectives=[
            f"理解{state.target_algorithm}的适用场景",
            "完成训练集/测试集划分、模型训练与指标评估",
            "能解释生成结果中的关键指标含义",
        ],
        explanation_strategy=strategy,
    )
    state.agent_events.append({
        "agent": "学情诊断 Agent",
        "status": "completed",
        "summary": f"识别出 {len(weak_points)} 个薄弱点，推荐难度为 {recommended_level}",
    })
    return state
