# AgentEdu 项目代码审查与后续开发交接文档

> 本文档用于交接给后续负责写代码的 AI。重点是从企业级软件开发视角审查当前代码、评价方案 v2 与 `plans/` 目录下的设计，并给出后续开发优先级。本文不考虑现场演示约束，只关注系统架构合理性、长期可维护性、模块集成和工程落地。

---

## 1. 项目当前定位

当前项目路径：

```text
E:/挑战杯/agent_edu_platform
```

项目目标是构建一个面向垂直领域技能培训的智能学习系统，当前垂直领域选择为：

```text
机器学习入门实训
```

核心闭环目标：

```text
学习者画像 → 多 Agent 协同 → RAG 检索 → 个性化资源生成 → 审核纠偏 → 反馈迭代 → 评测报告 → 跨会话学习进度沉淀
```

当前代码已经具备一个初步 demo，包括：

- LangGraph 多 Agent 工作流
- 规则版学情诊断
- 关键词 RAG 检索
- LLM + fallback 的资源生成
- 审核纠偏 Agent
- 反馈决策 Agent
- 规则版评测指标
- Streamlit demo
- Vue 3 静态前端原型
- SQLite + SQLAlchemy 数据库基础设施
- FAISS 向量库基础设施
- NetworkX 知识图谱基础设施

但需要注意：

> 当前很多基础设施已经写出来，但还没有真正接入主业务闭环。后续开发重点不应该继续横向堆新模块，而应该把数据库、FAISS、知识图谱、Vue 前端和 LangGraph 会话流真正集成起来。

---

## 2. 当前代码总体评价

### 2.1 当前成熟度

从长期工程化视角看，当前项目处于：

```text
可运行 demo + 局部基础设施已落地 + 方案设计较完整，但主链路集成不足
```

当前代码不是不能跑，而是存在明显的“设计层”和“实现层”断层：

| 模块 | 设计目标 | 当前实际状态 |
|---|---|---|
| LangGraph | 事件驱动、多轮对话循环图 | 当前是一次性生成流程 |
| 数据库 | 作为主数据源，支撑跨会话 | 表和初始化脚本已写，但 API 未接入 |
| RAG | FAISS + 关键词混合检索 | FAISS 已写，但主流程仍用关键词检索 |
| 知识图谱 | 路径规划、掌握度推荐、图谱 API | 模块已写，但未接入 Agent/API |
| Vue 前端 | 调用后端、展示真实资源和 Agent 状态 | 当前主要是静态高保真 UI |
| Session | 持久化学习会话 | 模型已设计，但主流程未使用 |
| Message | 对话历史入库 | 表已建，但未写入 |
| QuizAttempt | 答题记录与 mastered_points 更新 | 表已建，但未接入反馈逻辑 |

### 2.2 已验证结果

当前基础测试通过：

```bash
python -m pytest agent_edu_platform/tests
```

结果：

```text
3 passed
```

Vue 前端构建通过：

```bash
npm --prefix agent_edu_platform/frontend-vue run build
```

结果：构建成功，但存在包体较大的 warning，当前阶段不阻塞。

数据库初始化脚本可运行：

```bash
python agent_edu_platform/scripts/init_db.py
```

结果：数据库表可创建，JSON 学习者画像可迁移。

---

## 3. 当前目录结构审查

当前主要结构如下：

```text
agent_edu_platform/
├── agents/                 # 多 Agent 与 LangGraph 工作流
├── backend/                # FastAPI 后端接口与数据库基础设施
├── data/                   # 知识库、画像、知识图谱旧数据、SQLite 数据库
├── docs/                   # 文档
├── evaluation/             # 质量评测、幻觉检测、LLM Judge 占位
├── frontend/               # Streamlit 前端
├── frontend-vue/           # Vue 3 前端原型
├── knowledge_graph/        # NetworkX 知识图谱模块
├── rag_engine/             # 关键词检索、Embedding、FAISS 向量库
├── schemas/                # Pydantic 数据协议
├── scripts/                # 初始化、demo、向量库构建脚本
├── tests/                  # 测试
└── requirements.txt
```

结构整体是合理的，但存在几个问题：

1. `backend/` 已有数据库基础设施，但 API 还没有切换到数据库。
2. `rag_engine/` 同时存在关键词检索和 FAISS，但主流程只使用关键词检索。
3. `knowledge_graph/` 是独立模块，尚未接入诊断、生成、反馈或 API。
4. `frontend-vue/` 中存在 `node_modules/`，不应进入版本管理。
5. `__pycache__/`、`.pytest_cache/`、数据库文件、向量索引文件等应通过 `.gitignore` 排除。
6. `frontend/` 和 `frontend-vue/` 同时存在是可以接受的，但需要明确：Streamlit 是旧 demo，Vue 是长期产品化前端。

---

## 4. LangGraph 与 Agent 工作流审查

核心文件：

```text
agents/graph.py
agents/graph_state.py
agents/workflow.py
agents/state.py
agents/diagnosis_agent.py
agents/retrieval_agent.py
agents/generator_agent.py
agents/reviewer_agent.py
agents/feedback_agent.py
```

当前流程：

```text
START
  ↓
diagnosis
  ↓
retrieval
  ↓
generation
  ↓
review
  ↓
review 通过 → feedback
review 不通过且 retry_count < MAX_RETRY → generation
review 不通过但 retry_count >= MAX_RETRY → feedback
  ↓
evaluate
  ↓
END
```

## 4.1 优点

### 4.1.1 编排层和业务层基本分离

`agents/graph.py` 负责流程编排，各个 `*_agent.py` 负责具体业务逻辑。这是正确的方向。

### 4.1.2 资源生成支持 LLM + fallback

`agents/generator_agent.py` 中有：

```python
resources = _llm_generation(...)
if resources is None:
    resources = _fallback_generation(...)
```

这对长期开发很重要。即使模型调用失败，系统也能保持可用。

### 4.1.3 初步体现了学习者差异化

当前 fallback 生成已经区分：

- `beginner_plus`
- `intermediate`
- `advanced`

不同级别对应不同理论深度、代码复杂度和练习内容。

## 4.2 问题

### 4.2.1 当前流程还是一次性批处理，不是对话式 Agent 系统

当前 `run_workflow(profile)` 会一次性跑完整个图，然后结束。

但方案 v2 的目标是多轮对话式流程：

```text
init_session
  ↓
diagnosis
  ↓
retrieval
  ↓
generation
  ↓
review
  ↓
evaluate
  ↓
respond
  ↓
wait_for_user_input
  ↓
router_node
  ↓
answer_node / quiz_node / feedback_node / new_topic_node
  ↓
respond
  ↓
继续等待用户输入
```

因此后续需要新增会话型 LangGraph，而不是继续在当前一次性图上硬塞多轮逻辑。

### 4.2.2 当前 State 不支持会话上下文

当前 `WorkflowState` 主要字段：

```python
learner_id
learner_profile
target_algorithm
diagnosis
retrieved_knowledge
generated_resources
reviewer_feedback
review_passed
feedback_decision
evaluation
agent_events
retry_count
```

后续需要扩展为会话级 State，至少增加：

```python
session_id: str
user_message: str
conversation_summary: str
mastered_points: list[str]
current_phase: str
next_action: str
response_text: str
```

建议不要直接破坏现有 `WorkflowState`，可以新增：

```text
schemas/session_schema.py
schemas/chat_schema.py
```

并逐步扩展 `AgentGraphState`。

---

## 5. 数据库设计与实现审查

相关文件：

```text
backend/database.py
backend/models.py
scripts/init_db.py
plans/backend_db_plan.md
```

当前数据库方案设计 4 张核心表：

```text
Learner
Session
Message
QuizAttempt
```

## 5.1 设计评价

整体设计合理，适合长期开发。

| 表 | 作用 |
|---|---|
| `Learner` | 存储学习者长期画像、薄弱点、已掌握知识点 |
| `Session` | 存储一次学习会话的状态快照 |
| `Message` | 存储对话历史和 Agent 事件 |
| `QuizAttempt` | 存储答题记录，用于更新知识掌握度 |

这个设计可以支撑：

- 跨会话学习进度
- 历史对话恢复
- 学习报告生成
- 知识点掌握度更新
- 个性化推荐

## 5.2 当前实现问题

### 5.2.1 数据库未接入 API

当前 `backend/api/learner.py` 仍然从 JSON 文件读取学习者画像：

```python
PROFILE_DIR = PROJECT_ROOT / "data" / "learner_profiles"
```

说明数据库虽然已经建好，但主业务仍未使用它。

后续应优先把 API 改为从数据库读取。

### 5.2.2 JSON 字段 default 写法应调整

当前 `backend/models.py` 中存在：

```python
test_scores = Column(JSON, default={})
known_skills = Column(JSON, default=[])
weak_points = Column(JSON, default=[])
mastered_points = Column(JSON, default=[])
```

建议改为：

```python
test_scores = Column(JSON, default=dict)
known_skills = Column(JSON, default=list)
weak_points = Column(JSON, default=list)
mastered_points = Column(JSON, default=list)
```

避免可变默认值带来的潜在问题。

### 5.2.3 ORM 模型缺少 relationship

建议后续补充：

```python
Learner.sessions
Session.messages
Session.quiz_attempts
```

这会让 service 层查询更自然。

### 5.2.4 不建议当前阶段引入 Alembic

长期企业项目应该使用 Alembic 做迁移。但当前阶段重点是打通主链路，不建议过早引入迁移系统。等表结构稳定后再加。

## 5.3 数据库后续开发建议

优先实现：

```text
backend/services/learner_service.py
backend/services/session_service.py
schemas/session_schema.py
backend/api/session.py
```

最小 API：

```text
GET  /learners/examples          从数据库返回学习者列表
GET  /learners/{learner_id}      获取学习者画像
POST /sessions                   创建学习会话
GET  /sessions/{session_id}      获取会话快照
GET  /sessions/{session_id}/messages
```

当前不建议优先做 JWT。先完成 session 和数据闭环更重要。

---

## 6. RAG 设计与实现审查

相关文件：

```text
rag_engine/retriever.py
rag_engine/embedding.py
rag_engine/vector_store.py
scripts/build_vector_store.py
plans/rag_engine_plan.md
```

## 6.1 当前状态

当前主流程实际使用的是关键词检索：

```python
retrieval_agent.py → retrieve_knowledge(query) → rag_engine/retriever.py
```

`embedding.py`、`vector_store.py`、`build_vector_store.py` 已经写出，但还没有接入主流程。

## 6.2 RAG 方案评价

使用：

```text
BAAI/bge-small-zh-v1.5 + faiss-cpu
```

是合理的。

原因：

- 中文语义检索效果较好
- 本地运行，不依赖外部向量数据库
- 不需要部署 Milvus / Chroma 服务
- 适合中小规模知识库
- 方便后续迁移到更强向量数据库

## 6.3 当前实现优点

### 6.3.1 已考虑 Windows 中文路径问题

`vector_store.py` 在读写 FAISS 索引时通过临时英文路径规避 Windows 中文路径问题，这是一个重要工程细节。

### 6.3.2 向量库封装方向正确

当前 `FaissVectorStore` 提供：

```python
load()
save()
add_documents()
search()
```

接口设计基本合理。

## 6.4 当前问题

### 6.4.1 FAISS 未接入 `retrieve_knowledge`

现在主流程没有使用向量检索。

后续应改造成：

```python
def retrieve_knowledge(query: str, limit: int = 3) -> list[KnowledgeEvidence]:
    if vector_store_exists():
        return hybrid_retrieve(query, limit)
    return keyword_retrieve(query, limit)
```

### 6.4.2 应保留关键词 fallback

不要直接用 FAISS 替换关键词检索。推荐最终结构：

```text
retrieve_knowledge
├── vector_search     语义检索
├── keyword_search    关键词兜底
└── merge/rerank      合并去重排序
```

### 6.4.3 文档中的向量维度描述不一致

`vector_store.py` 默认：

```python
vector_dim = 512
```

`embedding.py` 注释也提到 bge-small-zh-v1.5 通常为 512 维。

但 `plans/rag_engine_plan.md` 里还有 768 维描述。建议统一改为 512。

### 6.4.4 `build_vector_store.py` 缺少 rebuild 模式

当前脚本多次执行可能重复追加同一批文档。

建议增加：

```python
build_index(rebuild: bool = True)
```

默认重建索引，而不是追加。

### 6.4.5 metadata 需要增强

当前向量元数据建议扩展为：

```python
{
    "chunk_id": "...",
    "source_id": "...",
    "source_path": "...",
    "title": "...",
    "content": "...",
    "knowledge_points": [...],
    "heading": "..."
}
```

这样后续可以做证据追溯、前端引用展示和评测。

---

## 7. 知识图谱设计与实现审查

相关文件：

```text
knowledge_graph/graph_builder.py
knowledge_graph/data/ml_knowledge_graph.json
plans/kg_plan.md
```

## 7.1 设计评价

知识图谱方向非常合理，适合长期发展。

它可以支撑：

- 前置知识追踪
- 个性化学习路径
- 掌握点高亮
- 知识点推荐
- 诊断解释增强
- 资源生成规划

## 7.2 当前实现能力

`KnowledgeGraphManager` 当前支持：

```python
get_prerequisites(target_node)
recommend_next_node(target_node, mastered_nodes)
get_subgraph_for_visualization()
```

这是一个不错的起点。

## 7.3 当前问题

### 7.3.1 未接入主流程

当前知识图谱模块没有被：

- `diagnosis_agent.py`
- `generator_agent.py`
- `feedback_agent.py`
- FastAPI API
- Vue 前端

调用。

所以它目前仍是孤立模块。

### 7.3.2 `get_prerequisites()` 只返回直接前置

当前函数只查一层前置节点。

建议增加：

```python
def get_all_prerequisites(target_node: str) -> list[str]
```

返回完整前置链。

### 7.3.3 应增加完整学习路径推荐

当前：

```python
recommend_next_node(...)
```

只返回一个节点。

长期更需要：

```python
recommend_learning_path(target_node, mastered_nodes) -> list[str]
```

返回完整路径，例如：

```text
Python 基础 → NumPy → 线性代数 → Sigmoid → 逻辑回归
```

## 7.4 后续集成建议

优先把知识图谱接入 `generator_agent.py` 的 `learning_path` 字段。

这样现有 workflow 不需要大改，就能让生成资源真正基于知识图谱。

---

## 8. 前端审查

当前有两套前端：

```text
frontend/          Streamlit
frontend-vue/      Vue 3
```

## 8.1 Streamlit 前端

`frontend/app.py` 当前已经能展示：

- 学习者画像
- RAG 检索证据
- Agent 流程
- 审核意见
- 个性化资源
- 学习路径
- 测试题答案解析
- 评测指标
- 反馈决策

这部分可以作为快速验证前端继续保留。

## 8.2 Vue 前端

当前 Vue 前端已经有：

```text
LoginView.vue
LearningView.vue
router/index.ts
main.ts
```

视觉效果不错，但目前主要是静态 UI 原型。

问题：

1. 没有调用 FastAPI。
2. 没有 axios API 封装。
3. 没有 Pinia store 实际业务状态。
4. 没有 session 管理。
5. 没有 SSE。
6. 没有真实 Agent 事件流。
7. 没有真实 RAG 证据渲染。
8. 没有真实生成资源渲染。

## 8.3 Vue 后续建议

不要一开始就做完整 SSE 对话。

建议先让 Vue 调通最小真实接口：

```text
POST /generation/run
```

拿到：

```python
generated_resources
agent_events
retrieved_knowledge
evaluation
feedback_decision
```

然后渲染到 `LearningView.vue`。

等这个通了，再做：

```text
/session
/chat/{session_id}
SSE
router agent
```

---

## 9. 方案 v2 评价

方案 v2 的总体方向是正确的，已经从“资料生成 demo”升级成了“对话式自适应学习系统”的产品架构。

## 9.1 方案 v2 中合理的设计

### 9.1.1 交互形态合理

```text
左侧对话 + 右侧资源面板
```

这种结构适合教育系统：

- 左侧承载多轮学习互动
- 右侧承载结构化资源、代码、题目、路径和图谱

### 9.1.2 双层 State 设计合理

方案 v2 区分：

```text
数据库持久层：Learner / Session / Message / QuizAttempt
LangGraph 运行态：当前轮上下文 + 摘要 + Agent 产出
```

这非常重要。

完整对话历史不应该放在 LangGraph State 中，而应该放数据库。State 中只保留：

```python
conversation_summary
user_message
current_phase
当前 Agent 输出
```

### 9.1.3 事件驱动 LangGraph 是正确方向

方案中设计：

```text
wait_for_user_input
router_node
answer_node
quiz_node
new_topic_node
feedback_node
```

这是从一次性 workflow 走向真正 Agent 应用的关键。

### 9.1.4 SSE 事件设计合理

建议保留这些事件类型：

```text
agent_start
agent_done
token
resource_update
quiz
done
error
```

### 9.1.5 渐进式升级原则正确

方案 v2 中写到不推翻现有代码，而是在现有 Agent、Schema、RAG、评测基础上扩展，这是正确原则。

## 9.2 方案 v2 中需要收敛的地方

方案 v2 范围偏大，同时包含：

- Vue 3
- Element Plus
- Pinia
- Vue Router
- FastAPI
- SQLite
- SQLAlchemy
- JWT
- SSE
- LangGraph interrupt
- Router Agent
- FAISS
- sentence-transformers
- 知识图谱
- LLM-as-Judge
- 评测报告
- 50+ 知识库
- Docker

长期方向没问题，但后续开发不能同时推进所有内容。

应分成：

```text
核心闭环优先
工程增强其次
产品体验最后
```

## 9.3 当前不建议优先做的内容

暂时不建议优先做：

```text
JWT 认证
Docker
完整后台管理
复杂权限
过多知识库扩充
完整 LLM-as-Judge 评测体系
复杂图谱算法
```

原因：这些内容不会先解决当前最关键的断层：

```text
数据库、RAG、知识图谱、Vue、LangGraph 会话流还没有集成进主链路。
```

---

## 10. `plans/` 目录设计评价

## 10.1 `backend_db_plan.md`

评价：合理，应该继续推进。

优点：

- SQLite + SQLAlchemy 适合当前阶段。
- Learner / Session / Message / QuizAttempt 四表设计合理。
- JSON 画像迁移脚本设计合理。
- 支撑跨会话学习状态。

需要调整：

1. 不要彻底废弃 JSON 文件，保留为 seed data 和 fallback。
2. API 应尽快切换到数据库。
3. JSON 字段默认值改为 `default=dict` / `default=list`。
4. 后续补 relationship。
5. 当前不急着引入 Alembic。

## 10.2 `rag_engine_plan.md`

评价：方向合理，但实现策略应改为混合检索。

建议最终结构：

```text
retrieve_knowledge(query)
├── 如果 FAISS index 存在：vector_search
├── 同时执行 keyword_search
├── merge / deduplicate / rerank
└── 返回 KnowledgeEvidence
```

需要调整：

1. 文档中的 768 维统一改为 512 维。
2. `build_vector_store.py` 加 rebuild 模式。
3. metadata 增加 chunk_id、source_path、knowledge_points。
4. `retriever.py` 保留关键词 fallback。

## 10.3 `kg_plan.md`

评价：合理，是系统长期价值的重要模块。

需要调整：

1. 增加完整前置链查询。
2. 增加完整学习路径推荐。
3. 先接入 `generated_resources.learning_path`。
4. 再做知识图谱 API。
5. 最后接 Vue 可视化。

---

## 11. 后续开发优先级

下面是建议给开发 AI 执行的优先级顺序。

---

## Phase 1：工程清理和基础稳定

### 目标

让项目结构更干净，避免缓存、依赖和生成文件污染版本管理。

### 任务

1. 添加或完善 `.gitignore`：

```gitignore
__pycache__/
*.pyc
.pytest_cache/
.env
agent_edu_platform/data/*.db
agent_edu_platform/data/vector_store/
agent_edu_platform/frontend-vue/node_modules/
agent_edu_platform/frontend-vue/dist/
```

2. 检查 `requirements.txt`，去掉重复依赖。

当前发现：

```text
networkx>=3.3
networkx>=3.0
```

应只保留一个，例如：

```text
networkx>=3.3
```

3. 增加集中配置模块，例如：

```text
backend/config.py
```

管理：

```python
APP_ENV
DATABASE_URL
DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL
DEEPSEEK_MODEL
VECTOR_STORE_PATH
EMBEDDING_MODEL_NAME
```

---

## Phase 2：数据库接入主业务

### 目标

让数据库成为后端主数据源，而不是只存在初始化脚本里。

### 任务

1. 修改 `backend/models.py`：

```python
Column(JSON, default=dict)
Column(JSON, default=list)
```

2. 新增 service 层：

```text
backend/services/learner_service.py
backend/services/session_service.py
```

3. 新增 schema：

```text
schemas/session_schema.py
```

4. 修改 learner API：

```text
GET /learners/examples
GET /learners/{learner_id}
```

改为从数据库读取。

5. 新增 session API：

```text
POST /sessions
GET  /sessions/{session_id}
GET  /sessions/{session_id}/messages
```

6. 暂时不要做 JWT，先用 `learner_id` 显式传参。

---

## Phase 3：FAISS 混合检索接入主流程

### 目标

让现有 `retrieval_agent.py` 不需要大改，但底层 `retrieve_knowledge()` 自动使用向量检索能力。

### 任务

1. 重构 `rag_engine/retriever.py`：

```python
def keyword_retrieve(query: str, limit: int) -> list[KnowledgeEvidence]
def vector_retrieve(query: str, limit: int) -> list[KnowledgeEvidence]
def hybrid_retrieve(query: str, limit: int) -> list[KnowledgeEvidence]
def retrieve_knowledge(query: str, limit: int = 3) -> list[KnowledgeEvidence]
```

2. 如果 FAISS 索引不存在，则自动 fallback 到关键词检索。

3. 修改 `scripts/build_vector_store.py`，默认 rebuild。

4. 扩展 metadata：

```python
chunk_id
source_id
source_path
title
content
knowledge_points
heading
```

5. 增加测试：

```text
tests/test_vector_store.py
tests/test_hybrid_retriever.py
```

---

## Phase 4：知识图谱接入生成链路

### 目标

让知识图谱真正影响学习路径，而不是孤立模块。

### 任务

1. 扩展 `KnowledgeGraphManager`：

```python
get_all_prerequisites(target_node: str) -> list[str]
recommend_learning_path(target_node: str, mastered_nodes: list[str]) -> list[str]
```

2. 将知识图谱接入 `generator_agent.py`：

```python
resources.learning_path = graph_recommended_path + existing_path
```

3. 或者接入 `diagnosis_agent.py`，根据 weak_points 和 graph 推断前置知识缺口。

4. 增加测试：

```text
tests/test_knowledge_graph.py
```

---

## Phase 5：Vue 前端接入真实后端数据

### 目标

让 Vue 从静态 UI 变成真实前端。

### 任务

1. 新增 API 封装：

```text
frontend-vue/src/api/index.ts
```

2. 新增 Pinia store：

```text
frontend-vue/src/stores/learner.ts
frontend-vue/src/stores/session.ts
frontend-vue/src/stores/generation.ts
```

3. `LoginView.vue` 调用后端 learner/session API。

4. `LearningView.vue` 先调用：

```text
POST /generation/run
```

并渲染真实：

```python
agent_events
retrieved_knowledge
generated_resources
evaluation
feedback_decision
```

5. 暂时不做 SSE，先完成普通 HTTP 闭环。

---

## Phase 6：会话型 LangGraph 和对话流

### 目标

从一次性 workflow 升级到多轮对话 Agent 系统。

### 任务

1. 新增：

```text
agents/router_agent.py
```

负责意图分类：

```text
ask_question
submit_quiz
request_hint
too_hard
too_easy
next_topic
end
general_chat
```

2. 扩展 `AgentGraphState`：

```python
session_id
user_message
conversation_summary
mastered_points
current_phase
next_action
response_text
```

3. 新增会话图，例如：

```text
agents/chat_graph.py
```

不要直接破坏现有 `graph.py`。

4. 新增节点：

```text
init_session_node
router_node
answer_node
quiz_node
new_topic_node
respond_node
```

5. 将 `Message` 写入数据库。

6. 将 `QuizAttempt` 写入数据库，并更新 `Learner.mastered_points`。

---

## Phase 7：SSE 流式接口

### 目标

让后端可以向 Vue 推送 Agent 状态、token 和资源更新。

### 任务

1. 新增：

```text
backend/api/chat.py
backend/services/chat_service.py
```

2. 设计 SSE event：

```text
agent_start
agent_done
token
resource_update
quiz
done
error
```

3. Vue 前端接入 SSE。

4. 只有当普通 HTTP 版本稳定后，再做 SSE。

---

## 12. 不建议后续 AI 立刻做的事

以下事项暂时不要优先做：

1. 不要马上引入 JWT。
2. 不要马上引入 Docker。
3. 不要马上做复杂后台管理。
4. 不要马上扩充 50-80 篇知识库。
5. 不要马上引入完整 LLM-as-Judge。
6. 不要把现有 workflow 全部推倒重写。
7. 不要删除 Streamlit 前端，它仍然适合快速验证。
8. 不要把关键词检索删除，应作为 fallback 保留。
9. 不要让 Vue 一开始就直接做 SSE，先普通 HTTP 联调。
10. 不要把所有历史 message 塞进 LangGraph State。

---

## 13. 给写代码 AI 的核心原则

请严格遵守：

1. 当前项目方向是长期工程化系统，不以现场演示为第一目标。
2. 不要继续横向新建太多模块，优先集成已有模块。
3. `agents/graph.py` 保留当前一次性 workflow，可新增 `chat_graph.py` 承载多轮对话。
4. 数据库要逐步成为主数据源。
5. JSON learner profiles 保留为 seed data 和 fallback。
6. RAG 要做 hybrid，不要删除 keyword fallback。
7. 知识图谱先接 learning_path，再做 API 和前端可视化。
8. Vue 先接普通 HTTP API，再做 SSE。
9. LLM 调用必须保留 fallback。
10. Message 历史必须入库，LangGraph State 只放摘要。
11. 代码应增加 service 层，避免 API 直接写业务逻辑。
12. 每完成一个模块都补最小测试。

---

## 14. 推荐下一步直接执行的开发任务

如果只能选一个最优先任务，建议先做：

```text
数据库接入 learner/session API
```

原因：

- 它是跨会话、对话历史、答题记录、掌握点更新的基础。
- 它能把当前数据库基础设施从“已写但未用”变成“主链路的一部分”。
- 它对后续 chat、SSE、Vue、评测报告都有依赖。

建议第一批代码任务：

```text
1. 修正 backend/models.py 的 JSON default
2. 新增 schemas/session_schema.py
3. 新增 backend/services/learner_service.py
4. 新增 backend/services/session_service.py
5. 修改 backend/api/learner.py 从 DB 读取
6. 新增 backend/api/session.py
7. 在 backend/main.py include session router
8. 增加 tests/test_session_api.py 或 tests/test_db_services.py
```

第二批任务再做：

```text
FAISS hybrid retriever 接入 retrieve_knowledge()
```

第三批任务做：

```text
知识图谱 learning_path 接入 generator_agent.py
```

第四批任务做：

```text
Vue LearningView 调用真实 /generation/run
```

---

## 15. 最终判断

当前方案 v2 是合理的，`plans/` 下的数据库、RAG、知识图谱设计也基本合理。

但当前最关键的工程问题是：

```text
基础设施模块已经分散写出，但尚未形成统一主链路。
```

后续开发应该围绕“集成”展开，而不是继续扩写新概念。

推荐主线：

```text
数据库主数据源
  ↓
Session 化 workflow
  ↓
Hybrid RAG
  ↓
知识图谱学习路径
  ↓
Vue 真实数据渲染
  ↓
多轮对话 chat graph
  ↓
SSE 流式交互
```

只要按这个顺序推进，项目会从当前 demo 逐步演进成一个结构清晰、可维护、可持续扩展的企业级 Agent 教育系统。
