from __future__ import annotations

from dataclasses import dataclass
from typing import Any


FOUNDATION_NODES = [
    "python_basics",
    "numpy_basics",
    "pandas_basics",
    "ml_task_framing",
    "tabular_data_understanding",
    "missing_value_handling",
    "categorical_encoding",
    "feature_scaling",
    "train_validation_test_split",
    "sklearn_workflow",
]

BRANCH_NODES: dict[str, list[str]] = {
    "common_foundation": FOUNDATION_NODES,
    "classification": [
        "sigmoid_function",
        "cross_entropy_loss",
        "logistic_regression",
        "model_evaluation_metrics",
        "confusion_matrix",
        "precision_recall_f1",
        "roc_auc_pr_curve",
        "cross_validation",
        "regularization",
    ],
    "regression": [
        "linear_regression",
        "regression_metrics",
        "polynomial_regression",
        "ridge_lasso",
        "cross_validation",
        "learning_validation_curve",
        "model_persistence",
    ],
    "model_explanation": [
        "decision_tree",
        "tree_pruning",
        "random_forest",
        "gradient_boosting",
        "model_evaluation_metrics",
        "confusion_matrix",
        "cross_validation",
        "model_persistence",
    ],
    "unsupervised": [
        "pca_dimensionality_reduction",
        "kmeans_clustering",
        "clustering_evaluation",
        "dbscan_clustering",
    ],
    "deep_learning_intro": [
        "neural_network_intro",
        "forward_backward_propagation",
        "activation_functions",
        "keras_sequential_intro",
        "deep_learning_regularization",
    ],
}

BRANCH_META: dict[str, dict[str, str]] = {
    "common_foundation": {
        "title": "共同基础",
        "description": "补齐 Python、数据处理、任务理解和 sklearn 建模流程。",
    },
    "classification": {
        "title": "分类预测",
        "description": "学习如何判断样本属于哪一类，并掌握分类指标。",
    },
    "regression": {
        "title": "连续值预测",
        "description": "学习如何预测连续数值，并理解回归误差指标。",
    },
    "model_explanation": {
        "title": "模型解释与集成",
        "description": "学习树模型、集成模型和特征重要性。",
    },
    "unsupervised": {
        "title": "无监督探索",
        "description": "学习降维、聚类和数据结构发现。",
    },
    "deep_learning_intro": {
        "title": "深度学习入门",
        "description": "用神经网络和 Keras 体验深度学习建模。",
    },
}

TARGET_ALGORITHM_TO_DIRECTION = {
    "逻辑回归": "classification",
    "KNN": "classification",
    "朴素贝叶斯": "classification",
    "线性回归": "regression",
    "决策树": "model_explanation",
    "随机森林": "model_explanation",
    "支持向量机": "classification",
    "无监督学习": "unsupervised",
    "深度学习入门": "deep_learning_intro",
}

SKILL_NODE_MAP: dict[str, str] = {
    "Python基础": "python_basics",
    "Python 基础": "python_basics",
    "Python 基础语法": "python_basics",
    "Numpy/Pandas": "pandas_basics",
    "NumPy": "numpy_basics",
    "Pandas": "pandas_basics",
    "微积分": "calculus",
    "线性代数": "linear_algebra",
    "概率论": "probability",
    "逻辑回归": "logistic_regression",
    "深度学习": "neural_network_intro",
}

PYTHON_LEVEL_MASTERED = {
    "none": [],
    "basic": ["python_basics"],
    "data_basic": ["python_basics", "numpy_basics", "pandas_basics"],
    "script": ["python_basics", "numpy_basics", "pandas_basics", "tabular_data_understanding"],
}

MATH_LEVEL_MASTERED = {
    "fear_formula": [],
    "basic": [],
    "college_math": ["linear_algebra", "probability"],
    "derivation": ["linear_algebra", "probability", "calculus", "gradient_descent"],
}

ML_LEVEL_MASTERED = {
    "none": [],
    "concept": ["ml_task_framing"],
    "sklearn_demo": ["ml_task_framing", "train_validation_test_split", "sklearn_workflow"],
    "project": ["ml_task_framing", "tabular_data_understanding", "train_validation_test_split", "sklearn_workflow"],
}

LEVEL_MASTERED_NODES: dict[str, list[str]] = {
    "beginner": [],
    "beginner_plus": [],
    "intermediate": ["python_basics", "numpy_basics", "pandas_basics", "train_validation_test_split"],
    "advanced": [
        "python_basics",
        "numpy_basics",
        "pandas_basics",
        "linear_algebra",
        "probability",
        "train_validation_test_split",
        "sklearn_workflow",
    ],
}

NODE_STAGE_OVERRIDES = {
    "python_basics": "共同基础",
    "numpy_basics": "共同基础",
    "pandas_basics": "共同基础",
    "ml_task_framing": "共同基础",
    "tabular_data_understanding": "共同基础",
    "missing_value_handling": "共同基础",
    "categorical_encoding": "共同基础",
    "feature_scaling": "共同基础",
    "train_validation_test_split": "共同基础",
    "sklearn_workflow": "共同基础",
}


@dataclass(frozen=True)
class LearningPlan:
    direction: str
    final_target: str
    current_node: str
    current_name: str
    current_stage: str
    current_branch: str
    recommended_reason: str
    full_path: list[str]
    path_names: list[str]
    current_step_index: int
    total_steps: int
    next_name: str
    available_branches: list[dict[str, Any]]


def build_learning_plan(learner: dict[str, Any], target_algorithm: str, kg: Any) -> LearningPlan:
    mastered = infer_mastered_nodes(learner, learner.get("current_level", "beginner_plus"))
    direction = resolve_direction(learner, target_algorithm)
    full_path = build_path_for_direction(direction)
    current_node = recommend_current_node(full_path, mastered)
    path_names = [node_name(kg, node) for node in full_path]
    current_name = node_name(kg, current_node)
    current_step_index = full_path.index(current_node) + 1 if current_node in full_path else 1
    total_steps = max(1, len(full_path))
    next_name = path_names[current_step_index] if current_step_index < len(path_names) else ""
    current_stage = node_stage(current_node, direction)
    current_branch = BRANCH_META[direction]["title"] if current_node not in FOUNDATION_NODES else "共同基础"

    return LearningPlan(
        direction=direction,
        final_target=BRANCH_META[direction]["title"],
        current_node=current_node,
        current_name=current_name,
        current_stage=current_stage,
        current_branch=current_branch,
        recommended_reason=recommended_reason(learner, direction, current_node, mastered),
        full_path=full_path,
        path_names=path_names,
        current_step_index=current_step_index,
        total_steps=total_steps,
        next_name=next_name,
        available_branches=build_available_branches(mastered, direction),
    )


def resolve_direction(learner: dict[str, Any], target_algorithm: str) -> str:
    target_direction = learner.get("target_direction") or "system_recommended"
    if target_direction != "system_recommended":
        return target_direction

    if target_algorithm in TARGET_ALGORITHM_TO_DIRECTION:
        return TARGET_ALGORITHM_TO_DIRECTION[target_algorithm]

    if learner.get("ml_level") == "project" and learner.get("math_level") in {"college_math", "derivation"}:
        return "model_explanation"
    return "classification"


def build_path_for_direction(direction: str) -> list[str]:
    if direction == "common_foundation":
        return list(FOUNDATION_NODES)
    return _dedupe([*FOUNDATION_NODES, *BRANCH_NODES.get(direction, BRANCH_NODES["classification"])])


def recommend_current_node(full_path: list[str], mastered_nodes: list[str]) -> str:
    mastered = set(mastered_nodes)
    for node in full_path:
        if node not in mastered:
            return node
    return full_path[-1] if full_path else "ml_task_framing"


def infer_mastered_nodes(learner: dict[str, Any], profile_level: str) -> list[str]:
    mastered = set(learner.get("mastered_points", []))
    mastered.update(LEVEL_MASTERED_NODES.get(profile_level, []))
    mastered.update(PYTHON_LEVEL_MASTERED.get(learner.get("python_level", "basic"), []))
    mastered.update(MATH_LEVEL_MASTERED.get(learner.get("math_level", "basic"), []))
    mastered.update(ML_LEVEL_MASTERED.get(learner.get("ml_level", "none"), []))

    for skill in learner.get("known_skills", []):
        node = SKILL_NODE_MAP.get(skill)
        if node:
            mastered.add(node)

    for node, score in learner.get("knowledge_mastery", {}).items():
        if score >= 0.7:
            mastered.add(node)

    return list(mastered)


def build_available_branches(mastered_nodes: list[str], current_direction: str) -> list[dict[str, Any]]:
    mastered = set(mastered_nodes)
    branches: list[dict[str, Any]] = []
    foundation_missing = [node for node in FOUNDATION_NODES if node not in mastered]

    for branch_id, meta in BRANCH_META.items():
        nodes = BRANCH_NODES[branch_id]
        completed = sum(1 for node in nodes if node in mastered)
        progress = round(completed / max(1, len(nodes)), 2)
        locked_reason = ""
        if branch_id != "common_foundation" and len(foundation_missing) > 2:
            locked_reason = "建议先完成共同基础中的数据理解、特征处理和 sklearn 流程。"
        branches.append({
            "id": branch_id,
            "title": meta["title"],
            "description": meta["description"],
            "progress": progress,
            "recommended": branch_id == current_direction,
            "locked_reason": locked_reason,
        })

    return branches


def recommended_reason(learner: dict[str, Any], direction: str, current_node: str, mastered_nodes: list[str]) -> str:
    if current_node == "python_basics":
        return "你的 Python 基础仍较薄弱，系统建议先补齐基础语法，再进入数据处理。"
    if current_node in {"numpy_basics", "pandas_basics"}:
        return "机器学习实训需要先能处理数组和表格数据，因此当前优先补齐数据处理基础。"
    if current_node in {"ml_task_framing", "tabular_data_understanding"}:
        return "你需要先理解机器学习任务和表格数据结构，后续模型训练才不会变成机械套代码。"
    if current_node in FOUNDATION_NODES:
        return "这是后续所有分支都会用到的共同基础，完成后可以更自由地切换学习方向。"
    if learner.get("target_direction") == "system_recommended":
        return f"系统根据你的画像推荐进入“{BRANCH_META[direction]['title']}”分支，并选择当前节点作为下一步。"
    return f"你选择了“{BRANCH_META[direction]['title']}”方向，当前节点是该分支的关键前置能力。"


def node_name(kg: Any, node_id: str) -> str:
    return kg.nodes_meta.get(node_id, {}).get("name", node_id)


def node_stage(node_id: str, direction: str) -> str:
    if node_id in NODE_STAGE_OVERRIDES:
        return NODE_STAGE_OVERRIDES[node_id]
    return BRANCH_META[direction]["title"]


def _dedupe(nodes: list[str]) -> list[str]:
    seen = set()
    result = []
    for node in nodes:
        if node not in seen:
            seen.add(node)
            result.append(node)
    return result


def build_learning_tree(learner: dict[str, Any], target_algorithm: str, kg: Any) -> dict[str, Any]:
    """
    构建完整的树状学习路径，供前端渲染知识树。

    返回结构:
    {
        "trunk": [  # 共同基础主干
            {"id": "python_basics", "name": "Python 基础", "mastered": True, "is_current": False},
            ...
        ],
        "branches": [  # 各个分支
            {
                "id": "classification",
                "title": "分类预测",
                "description": "...",
                "recommended": True,
                "progress": 0.35,
                "nodes": [
                    {"id": "sigmoid_function", "name": "...", "mastered": False, "is_current": True},
                    ...
                ]
            },
            ...
        ],
        "current_node": "sigmoid_function",
        "current_branch": "classification",  # 或 "trunk"
        "direction": "classification",
        "recommended_reason": "..."
    }
    """
    mastered = set(infer_mastered_nodes(learner, learner.get("current_level", "beginner_plus")))
    direction = resolve_direction(learner, target_algorithm)

    # 在整个路径中找当前推荐节点
    full_path = build_path_for_direction(direction)
    current_node = recommend_current_node(full_path, list(mastered))

    # 判断当前节点在主干还是分支
    current_in_trunk = current_node in FOUNDATION_NODES
    current_branch_id = "trunk" if current_in_trunk else direction

    # 构建主干节点
    trunk_nodes = []
    for node_id in FOUNDATION_NODES:
        trunk_nodes.append({
            "id": node_id,
            "name": node_name(kg, node_id),
            "mastered": node_id in mastered,
            "is_current": node_id == current_node,
        })

    # 构建各分支
    branches = []
    for branch_id, meta in BRANCH_META.items():
        if branch_id == "common_foundation":
            continue  # 主干已单独处理

        branch_node_ids = BRANCH_NODES[branch_id]
        completed = sum(1 for n in branch_node_ids if n in mastered)
        progress = round(completed / max(1, len(branch_node_ids)), 2)
        is_recommended = branch_id == direction

        # 判断是否锁定（基础未完成 >2 个）
        foundation_missing = sum(1 for n in FOUNDATION_NODES if n not in mastered)
        locked_reason = ""
        if foundation_missing > 2:
            locked_reason = "建议先完成共同基础中的数据理解、特征处理和 sklearn 流程。"

        nodes = []
        for node_id in branch_node_ids:
            nodes.append({
                "id": node_id,
                "name": node_name(kg, node_id),
                "mastered": node_id in mastered,
                "is_current": node_id == current_node,
            })

        branches.append({
            "id": branch_id,
            "title": meta["title"],
            "description": meta["description"],
            "recommended": is_recommended,
            "progress": progress,
            "locked_reason": locked_reason,
            "nodes": nodes,
        })

    reason = recommended_reason(learner, direction, current_node, list(mastered))

    return {
        "trunk": trunk_nodes,
        "branches": branches,
        "current_node": current_node,
        "current_node_name": node_name(kg, current_node),
        "current_branch": current_branch_id,
        "direction": direction,
        "recommended_reason": reason,
    }

