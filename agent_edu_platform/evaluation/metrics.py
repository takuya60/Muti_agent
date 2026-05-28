from schemas.agent_state_schema import WorkflowState
from schemas.evaluation_schema import EvaluationResult


_EXPECTED_POINT_ALIASES = {
    "训练集": ["训练集", "X_train", "y_train", "train_test_split"],
    "测试集": ["测试集", "X_test", "y_test", "test set", "测试数据"],
    "标准化": ["标准化", "StandardScaler", "归一化", "缩放", "scaler"],
    "模型训练": ["模型训练", ".fit(", "fit(", "训练模型", "学习参数"],
    "准确率": ["准确率", "accuracy", "accuracy_score", "正确率"],
    "混淆矩阵": ["混淆矩阵", "confusion_matrix", "TP", "FP", "TN", "FN"],
}


def evaluate_resources(state: WorkflowState) -> EvaluationResult:
    resources = state.generated_resources or {}
    text = _flatten(resources)
    covered_points = [
        point
        for point, aliases in _EXPECTED_POINT_ALIASES.items()
        if any(alias in text for alias in aliases)
    ]
    covered = len(covered_points)
    coverage = covered / len(_EXPECTED_POINT_ALIASES)

    level = resources.get("learner_level", "beginner_plus")
    weak_count = len(state.diagnosis.weak_points if state.diagnosis else [])
    if weak_count >= 3 and level == "beginner_plus":
        difficulty_match = 0.9
    elif weak_count <= 1 and level in {"advanced", "intermediate"}:
        difficulty_match = 0.88
    else:
        difficulty_match = 0.78

    structure_keys = ["theory_note", "dataset_instruction", "practice_guide", "graded_quiz"]
    completeness = sum(1 for key in structure_keys if resources.get(key)) / len(structure_keys)
    hallucination_rate = 0.02 if state.review_passed else 0.12

    return EvaluationResult(
        hallucination_risk="low" if hallucination_rate < 0.05 else "medium",
        hallucination_rate=hallucination_rate,
        difficulty_match=difficulty_match,
        knowledge_coverage=coverage,
        structure_completeness=completeness,
        notes=[
            "当前指标为规则估算，后续可接入人工标注和 LLM-as-Judge。",
            f"覆盖知识点 {covered}/{len(_EXPECTED_POINT_ALIASES)}：{', '.join(covered_points)}。",
        ],
    )


def _flatten(value: object) -> str:
    if isinstance(value, dict):
        return "\n".join(_flatten(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(_flatten(item) for item in value)
    return str(value)
