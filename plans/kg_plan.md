# 知识图谱构建方案 (Phase 1.4)

现在我们进入**阶段 1 的第 4 项任务：构建知识点依赖图谱**。这也是我们产品的一大核心亮点：为学习者规划个性化的学习路径，并能在前端可视化展示（就像科技感十足的技能树）。

## 1. 为什么需要知识图谱？
传统的目录式学习是线性的。但在我们的系统中，如果诊断出用户的“线性代数”弱，我们不应该强行让他立刻学“逻辑回归”，而是沿着知识图谱回溯，推荐他先学前置知识点。

我们将引入 `networkx` 来进行有向无环图（DAG）的建模。

## 2. 依赖变更
将在 `requirements.txt` 中增加：
- `networkx>=3.0`

## 3. 核心文件设计

### `knowledge_graph/data/ml_knowledge_graph.json`
定义图谱数据的结构。我们将知识点分为：基础、数学、工程、模型、评估等类别。
数据格式设计如下：
```json
{
  "nodes": [
    {"id": "python", "name": "Python 基础", "category": "基础"},
    {"id": "numpy", "name": "NumPy 操作", "category": "基础"},
    {"id": "linear_algebra", "name": "线性代数", "category": "数学"},
    {"id": "logistic_regression", "name": "逻辑回归", "category": "模型"}
  ],
  "edges": [
    {"from": "python", "to": "numpy", "type": "prerequisite"},
    {"from": "numpy", "to": "linear_algebra", "type": "prerequisite"},
    {"from": "linear_algebra", "to": "logistic_regression", "type": "prerequisite"}
  ]
}
```

### `knowledge_graph/graph_builder.py`
提供 `KnowledgeGraphManager` 类，包含以下核心能力：
1. **加载图谱**：读取 JSON，实例化为 `networkx.DiGraph`。
2. **前置知识追踪 (`get_prerequisites`)**：查询学习目标的所有必修前置。
3. **学习路径推荐 (`recommend_next_node`)**：结合学习者画像中的 `mastered_points`，沿着图谱计算下一个应该学的节点是什么（避开已掌握的，直击未掌握的最近前置节点）。

## ❓ 开放问题与确认项
> [!IMPORTANT]
> 1. 目前我打算手工为您定义一份包含约 15-20 个核心机器学习入门知识点的 JSON 数据，足够我们在比赛中展示出**非常完整的技能树依赖和路径推荐效果**。您看这个规模可以吗？
> 2. 后端基于 NetworkX 算出路径后，后续阶段我们会把完整的图谱结构通过接口传给 Vue 前端，让前端用 ECharts 或 G6 画出非常炫酷的动态节点图。这个思路您认可吗？

请审阅此图谱构建方案，如果同意，我将为您生成节点数据和相关的核心算法代码！
