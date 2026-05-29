from rag_engine import retrieve_knowledge
from schemas.agent_state_schema import WorkflowState


_DIRECTION_QUERY_TERMS = {
    "system_recommended": "机器学习 入门 学习路径 数据处理 sklearn",
    "common_foundation": "Python NumPy Pandas 机器学习基础 数据处理 sklearn",
    "classification": "分类预测 逻辑回归 决策树 混淆矩阵 Precision Recall F1",
    "regression": "线性回归 回归指标 MAE MSE R2 Ridge Lasso",
    "model_explanation": "决策树 随机森林 GBDT 特征重要性 模型解释",
    "unsupervised": "PCA KMeans DBSCAN 聚类评估 无监督学习",
    "deep_learning_intro": "神经网络 Keras 前向传播 反向传播 早停 Dropout",
}


def run_retrieval_agent(state: WorkflowState) -> WorkflowState:
    profile = state.learner_profile
    diagnosis_terms = " ".join(state.diagnosis.weak_points if state.diagnosis else [])
    direction = profile.get("target_direction", "system_recommended")
    direction_terms = _DIRECTION_QUERY_TERMS.get(direction, _DIRECTION_QUERY_TERMS["system_recommended"])
    profile_terms = " ".join([
        profile.get("python_level", ""),
        profile.get("math_level", ""),
        profile.get("ml_level", ""),
        profile.get("practice_preference", ""),
        profile.get("theory_preference", ""),
        profile.get("current_confusion", ""),
    ])
    query = f"{state.target_algorithm} {direction_terms} {diagnosis_terms} {profile_terms} 训练 测试 评估 常见错误"
    state.retrieved_knowledge = retrieve_knowledge(query)
    state.agent_events.append({
        "agent": "知识检索 Agent",
        "status": "completed",
        "summary": f"围绕 {direction_terms} 检索到 {len(state.retrieved_knowledge)} 条知识库证据",
    })
    return state
