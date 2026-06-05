# 全 Agent LLM 驱动升级 — 设计文档

## 背景

当前 AgentEdu 多智能体流水线中，6 个 Agent 中仅「资源生成 Agent」由 DeepSeek LLM 驱动，其余 4 个核心 Agent（画像诊断、路径规划、审核纠偏、反馈规划）均为纯规则引擎（If-Else / 正则匹配）。

此外，知识图谱中的学习节点全部硬编码在 `path_planner.py` 和 `ml_knowledge_graph.json` 中（共约 50 个节点），无法动态扩展。

## 设计目标

1. 将 4 个规则 Agent 全部升级为 **LLM 优先 + 规则兜底** 的混合架构
2. 让路径规划 Agent 在每次 LLM 规划时都能**主动审视现有图谱**，自主判断是否需要补充或细化节点（例如把 "GBDT / XGBoost 思想" 拆分为两个独立节点，或在某个分支末尾补充进阶内容），无需用户主动提出

## 核心设计决策

| 决策点 | 选定方案 |
|---|---|
| 升级范围 | 画像诊断 + 路径规划 + 审核纠偏 + 反馈规划（共 4 个） |
| 容错策略 | LLM 优先，异常时自动降级到原有规则逻辑 |
| 输出格式控制 | DeepSeek + OpenAI SDK，`response_format={"type": "json_object"}` |
| 幻觉防护 | Prompt 中喂入合法枚举列表 + 代码后置校验过滤 |
| UI 可见性 | 前端抽屉和 SSE 终端明确标注 "LLM" 或 "规则降级" |
| 超时设置 | 全局统一 30 秒 |
| 动态节点 | LLM 可提议新节点，代码校验后写入 JSON 图谱文件 |

---

## 架构

### 新增公共服务层：`agents/llm_service.py`

抽取一个轻量的公共函数，统一管理 OpenAI client 初始化、API 调用、JSON 解析。所有 Agent 共用此入口，避免重复代码。

```python
# agents/llm_service.py
def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    timeout: float = 30.0,
    temperature: float = 0.3,
) -> dict:
    """
    调用 DeepSeek LLM 并返回解析后的 JSON dict。
    失败时抛出异常，由调用方决定如何 fallback。
    """
```

**职责边界**：
- `llm_service.py` 只负责「发送 prompt → 拿到 JSON dict」
- 各 Agent 自己负责「组装 prompt」和「解析 dict → 领域对象」
- 各 Agent 自己负责「try/except → fallback」

---

### 各 Agent 改造方案

#### 1. 画像诊断 Agent (`diagnosis_agent.py`)

**LLM 输入**：用户完整的 `learner_profile` JSON（包含 python_level、math_level、ml_level、current_confusion 等）

**LLM 输出 Schema**：
```json
{
  "weak_points": ["薄弱点1", "薄弱点2"],
  "strengths": ["优势1", "优势2"],
  "recommended_level": "beginner_plus",
  "learning_objectives": ["目标1", "目标2", "目标3"],
  "explanation_strategy": "先给任务场景和代码，再讲原理"
}
```

**守卫规则**：
- `recommended_level` 必须是枚举 `beginner / beginner_plus / intermediate / advanced` 之一，否则回退到 `beginner_plus`

**Fallback**：原有的 `_INITIAL_WEAK_POINTS` + `_LEVEL_LABELS` 规则映射逻辑（重命名为 `_fallback_diagnosis`）

---

#### 2. 路径规划 Agent (`path_planner.py`) + 动态节点扩展

这是改动最大的一个 Agent，分为两个子能力：

**子能力 A：智能分支选择和已掌握节点推断**

LLM 输入：用户画像 + 目标算法 + 完整的分支列表 + 各分支的节点列表

LLM 输出 Schema：
```json
{
  "target_direction": "classification",
  "mastered_nodes": ["python_basics", "numpy_basics"],
  "recommended_reason": "你已具备 Python 基础，推荐进入分类预测分支",
  "new_nodes": []
}
```

守卫规则：
- `target_direction` 必须存在于 `BRANCH_META` 中，否则回退到 `classification`
- `mastered_nodes` 中每个节点必须在已知节点集合中，不存在的直接过滤
- 拿到合法结果后，仍然交给现有的 `build_path_for_direction()` + `recommend_current_node()` 纯代码函数组装路径

**子能力 B：动态节点补充与细化**

LLM 在每次规划时都会审视当前图谱的节点覆盖度。如果它认为现有节点粒度不够细、覆盖不够全，或者用户的目标需要更精准的拆分，可以在 `new_nodes` 中主动提议补充：

```json
{
  "new_nodes": [
    {
      "id": "xgboost",
      "name": "XGBoost 梯度提升",
      "category": "集成学习",
      "branch": "model_explanation",
      "prerequisites": ["gradient_boosting", "cross_validation"]
    }
  ]
}
```

**动态节点的写入流程**：
1. 校验 `id` 不与已有节点冲突
2. 校验 `prerequisites` 中的节点都真实存在
3. 校验 `branch` 是合法的分支名
4. 写入 `ml_knowledge_graph.json`（追加 node 和 edge）
5. 动态更新内存中的 `BRANCH_NODES[branch]` 列表
6. 重新加载 `KnowledgeGraphManager` 的 networkx 图

**安全约束**：
- 每次最多新增 3 个节点（防止 LLM 一口气生成一大堆）
- 新节点的 `id` 必须是纯英文小写 + 下划线格式
- 如果写入失败，不影响本次路径规划（忽略新节点，继续用已有节点）

**Fallback**：原有的 `resolve_direction()` + `infer_mastered_nodes()` 逻辑（不支持动态节点）

---

#### 3. 审核纠偏 Agent (`reviewer_agent.py`)

**LLM 输入**：生成的资源 JSON（讲义摘要、代码片段、测验题目）+ 检索到的知识库证据标题

**LLM 输出 Schema**：
```json
{
  "passed": true,
  "issues": [],
  "summary": "审核通过：内容结构完整，引用来源准确，难度匹配合理"
}
```

**双重检查机制**：
无论 LLM 返回什么，代码层仍然执行以下**硬规则检查**：
- 数据泄露检测（`fit_transform(X_test)` 等禁止模式）
- 资源结构字段完整性检查（必须包含 `theory_note`, `practice_guide` 等 6 个字段）
- 测试题数量不少于 3 道
- 必须包含知识库引用来源

**合并逻辑**：代码硬规则发现的问题 + LLM 发现的问题取并集。只有两者都通过才判定为 `passed`。

**Fallback**：原有的纯规则检查逻辑

---

#### 4. 反馈规划 Agent (`feedback_agent.py`)

**LLM 输入**：测验准确率 + 用户反馈文本 + 当前资源的标题和难度级别

**LLM 输出 Schema**：
```json
{
  "next_action": "生成降维解释，补充前置知识",
  "resource_type": "remedial_explanation",
  "reason": "用户测验得分较低且反馈中提到概念理解困难"
}
```

**守卫规则**：
- `resource_type` 必须是枚举 `standard_practice / remedial_explanation / advanced_challenge / reinforcement` 之一

**Fallback**：原有的分数阈值 3 路判断逻辑

---

### SSE 流式终端显示

在 `agent_events` 的 `summary` 字段前缀标注引擎类型：
- LLM 成功时：`[LLM 诊断] 识别出 4 个薄弱点，策略：先给代码再讲原理`
- 降级时：`[规则降级] 识别出 3 个薄弱点，推荐难度 intermediate`
- 动态节点时：`[LLM 规划] 新增节点 xgboost → 已写入知识图谱`

---

### 数据流完整链路

```
用户画像 → [画像诊断 LLM] → DiagnosisResult
                                    ↓
用户画像 + 目标 + 图谱 → [路径规划 LLM] → direction + mastered + (new_nodes?)
                                                ↓ 写入图谱        ↓ 代码组装
                                         ml_knowledge_graph.json   LearningPlan
                                                                        ↓
query 拼接 → [知识检索 BGE 本地模型] → list[KnowledgeEvidence]     (不变)
                                    ↓
全部上下文 → [资源生成 LLM] → GeneratedResources                    (不变)
                                    ↓
资源 + 证据 → [审核纠偏 LLM + 代码双重检查] → review_passed
                                    ↓
分数 + 反馈 → [反馈规划 LLM] → feedback_decision
```

---

### 不变的部分

- `retrieval_agent.py`：保持本地向量模型检索不变
- `generator_agent.py`：已经是 LLM 驱动，本次不改
- `graph.py`：LangGraph 的节点定义和边拓扑不变
- `graph_state.py` / `state.py`：状态转换逻辑不变
- `agent_state_schema.py`：`DiagnosisResult` 和 `WorkflowState` 的字段定义不变
- `evaluation/metrics.py`：评测指标计算不变

### 新增文件

- `agents/llm_service.py`：公共 LLM 调用服务层

### 修改文件

- `agents/diagnosis_agent.py`：新增 `_llm_diagnosis()` + 重命名原逻辑为 `_fallback_diagnosis()`
- `agents/path_planner.py`：新增 `_llm_path_decision()` + 动态节点写入逻辑 + 重命名原逻辑
- `agents/reviewer_agent.py`：新增 `_llm_review()` + 保留原逻辑作为硬规则层
- `agents/feedback_agent.py`：新增 `_llm_feedback()` + 重命名原逻辑
- `knowledge_graph/graph_builder.py`：新增 `add_node()` 和 `save()` 方法支持动态写入
