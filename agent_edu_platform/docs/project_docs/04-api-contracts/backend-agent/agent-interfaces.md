# 后端 ↔ Agent 层内部接口文档

> 文档版本: v1.0 | 最后更新: 2026-06-22
>
> 本文档定义了后端服务层与 Agent 层之间的函数调用契约。Agent 开发者只需关注自己负责的 Agent 的输入/输出，无需了解 HTTP 路由细节。

---

## 一、公共状态总线 (`WorkflowState`)

所有 Agent 共享一个 Pydantic 状态对象，定义在 `schemas/agent_state_schema.py`：

```python
class WorkflowState(BaseModel):
    learner_id: str                                    # 学习者 ID
    learner_profile: dict                              # 完整画像字典
    target_algorithm: str                              # 目标算法 (如 "逻辑回归")
    diagnosis: DiagnosisResult | None = None           # 诊断 Agent 输出
    retrieved_knowledge: list[KnowledgeEvidence] = []   # 检索 Agent 输出
    generated_resources: dict | None = None            # 生成 Agent 输出
    reviewer_feedback: str = ""                        # 审核 Agent 反馈
    review_passed: bool = False                        # 审核是否通过
    feedback_decision: dict | None = None              # 反馈 Agent 决策
    evaluation: dict | None = None                     # 评估结果
    agent_events: list[dict] = []                      # Agent 执行日志 (供 SSE 推送)
    retry_count: int = 0                               # 当前重试次数
```

---

## 二、各 Agent 接口定义

### 2.1 诊断 Agent (`agents/diagnosis_agent.py`)

```python
def run_diagnosis_agent(state: WorkflowState) -> WorkflowState
```

**读取**: `state.learner_profile`

**写入**:
- `state.diagnosis` → `DiagnosisResult`
  - `weak_points: list[str]` — 诊断出的薄弱点
  - `strengths: list[str]` — 已有优势
  - `recommended_level: str` — 推荐级别 (`beginner` / `beginner_plus` / `intermediate` / `advanced`)
  - `learning_objectives: list[str]` — 学习目标
  - `explanation_strategy: str` — 解释策略描述
- `state.agent_events` ← 追加诊断事件

**行为**: 优先调用 LLM 进行深度诊断 (`_llm_diagnosis`)，失败时降级为规则引擎 (`_fallback_diagnosis`)

---

### 2.2 检索 Agent (`agents/retrieval_agent.py`)

```python
def run_retrieval_agent(state: WorkflowState) -> WorkflowState
```

**读取**: `state.target_algorithm`, `state.diagnosis`

**写入**:
- `state.retrieved_knowledge` → `list[KnowledgeEvidence]`
  - `source_id: str`
  - `title: str`
  - `content: str`
  - `knowledge_points: list[str]`
  - `score: float`
- `state.agent_events` ← 追加检索事件

---

### 2.3 生成 Agent (`agents/generator_agent.py`)

```python
def run_generator_agent(state: WorkflowState) -> WorkflowState
```

**读取**: `state.learner_profile`, `state.diagnosis`, `state.retrieved_knowledge`, `state.target_algorithm`

**写入**:
- `state.generated_resources` → `dict` (序列化后的 `GeneratedResources`)
  - `theory_note: str` — Markdown 讲义
  - `practice_guide: list[CodeStep]` — 代码实操步骤
  - `graded_quiz: list[QuizItem]` — 分阶测验
  - `learning_path: list[str]` — 学习路径
  - `citations: list[str]` — 引用来源
  - `agent_trace: AgentTrace` — Agent 执行轨迹
  - ... (完整定义见 `schemas/resource_schema.py`)
- `state.agent_events` ← 追加生成事件

**行为**: 优先 LLM 生成，失败时降级为规则模板

---

### 2.4 审核 Agent (`agents/reviewer_agent.py`)

```python
def run_reviewer_agent(state: WorkflowState) -> WorkflowState
```

**读取**: `state.generated_resources`, `state.retrieved_knowledge`

**写入**:
- `state.review_passed: bool` — 是否通过审核
- `state.reviewer_feedback: str` — 具体问题描述（多条用分号拼接）
- `state.agent_events` ← 追加审核事件

**行为**: 双重检查。先执行代码硬规则检查 (`_hard_rule_review`)，再调用 LLM 语义审核 (`_llm_review`)。两者发现的问题合并判定。

---

### 2.5 反馈 Agent (`agents/feedback_agent.py`)

```python
def run_feedback_agent(
    state: WorkflowState,
    quiz_accuracy: float | None = None,
    learner_feedback: str = ""
) -> WorkflowState
```

**读取**: 函数参数 `quiz_accuracy`, `learner_feedback`

**写入**:
- `state.feedback_decision` → `dict`
  - `quiz_accuracy: float | None`
  - `learner_feedback: str`
  - `next_action: str` — 下一步行动描述
  - `resource_type: str` — `standard_practice` | `remedial_explanation` | `advanced_challenge` | `reinforcement`
- `state.agent_events` ← 追加反馈事件

---

### 2.6 路径规划器 (`agents/path_planner.py`)

> 注意：路径规划器不是一个 LangGraph 节点，而是被 Generator Agent 和 API 层直接调用的工具函数。

```python
def build_learning_plan(learner: dict, target_algorithm: str, kg: KnowledgeGraphManager) -> LearningPlan

def build_learning_tree(learner: dict, target_algorithm: str, kg: KnowledgeGraphManager) -> dict
```

**内部决策流**: 优先调用 `_llm_path_decision` (LLM 推荐分支 + 动态注入新节点)，失败时降级为 `_fallback_resolve_direction` + `_fallback_infer_mastered_nodes`

---

## 三、LangGraph 工作流拓扑 (`agents/graph.py`)

```python
# 节点注册
graph.add_node("diagnosis", run_diagnosis_agent)
graph.add_node("retrieval", run_retrieval_agent)
graph.add_node("generation", run_generator_agent)
graph.add_node("review", run_reviewer_agent)
graph.add_node("feedback", run_feedback_agent)

# 边定义
diagnosis → retrieval → generation → review
review → (条件边) → generation (如果 review_passed=False 且 retry<3)
review → (条件边) → feedback (如果 review_passed=True)
feedback → END
```
