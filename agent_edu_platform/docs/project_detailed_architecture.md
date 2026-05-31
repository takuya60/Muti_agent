# 领域知识个性化生成与多智能体协同决策系统 - 详尽架构与技术白皮书

本白皮书旨在全面、深度地剖析 AgentEdu 系统的技术实现细节，从底层数据结构、算法逻辑到顶层架构设计进行系统性复盘。本文档将作为“挑战杯”评委技术审查及后续团队二次开发的核心参考手册。

---

## 〇、系统宏观架构

系统基于前后端分离与多智能体微服务架构，核心运转流如下：
1. **用户交互 (Vue3)** 发起学习请求。
2. **业务网关 (FastAPI)** 拦截请求，提取学习者画像与当前缓存状态。
3. **知识规划中枢 (NetworkX)** 计算出当前最优的学习节点。
4. **多 Agent 协同集群 (LangGraph)** 进行“诊断-检索-生成-审查”的异步工业化流水线作业。
5. 生成完毕后持久化至 **SQLite**，并返回前端渲染。

---

## 一、核心层级拆解与底层实现

### 1.1 知识图谱引擎 (Knowledge Graph Engine)
摒弃了传统的“章节列表”，系统采用了基于 `NetworkX` 的有向无环图 (DAG) 算法。
- **核心文件**：`knowledge_graph/graph_builder.py`
- **数据结构**：`nx.DiGraph()`
- **核心算法 `recommend_next_node`**：
  采用深度优先搜索 (DFS) / 广度优先搜索 (BFS) 变体进行逆向回溯。当用户选定目标节点（如 `logistic_regression`）时，算法会沿着 `prerequisite` 类型的边递归检查前置节点是否已被记录在 `mastered_nodes` 列表中。如果发现缺失的前置知识（如 `python_basics`），则**阻断**当前目标的生成，转而推荐最底层的基础节点，实现了真正的“因材施教”与“地基构建”。
- **分支拓展能力**：通过 `path_planner.py` 中的 `build_learning_tree` 方法，能够从图谱中剥离出“共同基础”作为主干（Trunk），将平行的高级概念（如计算机视觉、自然语言处理）切分为独立分支（Branches），支持前端树状渲染。

### 1.2 RAG 混合检索引擎 (Hybrid RAG Engine)
为了彻底解决大语言模型的“幻觉”现象，尤其是在代码与公式推导等严谨领域，系统内置了本地向量库。
- **核心文件**：`rag_engine/retriever.py`, `vector_store.py`
- **检索策略 `hybrid_retrieve`**：
  1. **向量检索优先 (FAISS)**：通过提取 query 的 Embeddings 去 `FaissVectorStore` 中进行高维空间相似度比对。同时引入了严格的阈值控制（`score < 0.3` 直接丢弃），执行“宁缺毋滥”策略。
  2. **关键词检索兜底 (Fallback)**：当本地尚未构建 FAISS 索引或向量服务宕机时，系统提供基于本地 Markdown 源文件的暴力关键词容灾机制。
  3. **数据契约封装**：无论采用哪种检索，最终统一输出 `KnowledgeEvidence` 的 Pydantic 实体，供下游 Agent 消费。

### 1.3 多智能体大脑 (Multi-Agent Workflow via LangGraph)
有别于暴力的 `Single Prompt` 模式，系统抽象出六个专业的 Agent，通过 `StateGraph` 进行流转。
- **状态总线 (`AgentGraphState`)**：包含 `learner_profile`、`agent_events`、`generated_resources`、`reviewer_feedback` 等，充当所有 Agent 共享的“黑板”。
- **流水线执行器**：
  - **`Diagnose Agent`**：分析能力雷达、弱点字典，确定当前上下文深度（Depth）。
  - **`Path Planner Agent`**：与上述知识图谱模块联动，确定微观路径。
  - **`Retrieval Agent`**：调用 RAG 模块，拼装领域知识片段。
  - **`Generator Agent`**：这是核心生产力，它接收前置的所有上下文（诊断报告+权威资料），生成 JSON 格式的讲义、代码示例与测验。
  - **`Review Agent`**（质量控制）：基于独立视角的“纠偏 Agent”。如果它判定 `Generator` 偏离了主题、出现了逻辑错误或幻觉，会将 `review_passed` 置为 `False`，状态机通过图论里的条件边（Conditional Edge）将流程**打回**给 `Generator` 重新生成，最多重试 N 次。

### 1.4 API 服务与缓存层 (FastAPI Backend)
- **精准缓存设计 (`backend/models.py` & `generation.py`)**：
  考虑到多 Agent 协同流程（生成-审查-重试）极其耗时且消耗 API Token，系统在 `Session` 表中创新性地引入了 `target_node` 字段。
  当接收到 `/generation/run` 请求时，算法首先计算得出 `current_node`。如果数据库中存在 `(learner_id == 当前学习者) AND (target_node == current_node) AND (资源非空)`，则**直接拦截请求**，毫秒级返回历史快照数据。
- **持久化画像 (`Learner`)**：除了基础信息，还存储了跨会话的 `bloom_taxonomy` (布鲁姆认知层级)、`frustration_index` (挫败感指数) 等深度增强画像字段（企业级扩展）。

### 1.5 沉浸式前端 (Vue 3 + Pinia)
- **视觉层 (`DashboardView` & `LearningPathView`)**：采用 Glassmorphism (玻璃拟态) 设计语言与 SVG 动态环形进度条，提升竞赛展示的科技感。
- **交互层**：学习树视图摒弃了生硬的列表，实现了类似 Git 分支的可视化节点图。
- **状态层 (`stores/generation.ts`)**：与后端的长耗时接口保持异步心跳，期间在界面上展示优雅的 Agent 运转过程动画，极大程度缓解了用户的等待焦虑。

---

## 二、项目目录结构全景解析

```text
agent_edu_platform/
├── agents/                       # 🧠 智能体逻辑层
│   ├── answer_agent.py           # - 负责“交互答疑”的 Agent
│   ├── diagnose_agent.py         # - 负责解析画像的 Agent
│   ├── generator_agent.py        # - 内容生成主力 Agent
│   ├── review_agent.py           # - 严格的质量审查 Agent
│   ├── path_planner.py           # - 树状路径编排与转化 Agent
│   ├── graph_state.py            # - LangGraph 状态黑板定义
│   └── workflow.py               # - 连接所有 Agent 的控制流向图
│
├── backend/                      # 🔌 服务与调度层
│   ├── api/                      # - REST 路由入口
│   │   ├── generation.py         #   - 控制生成触发与精准缓存
│   │   ├── learning_tree.py      #   - 树状结构获取与分支切换
│   │   └── session.py            #   - 状态查询
│   ├── models.py                 # - SQLite ORM 结构 (Learner, Session)
│   ├── database.py               # - 数据库连接池
│   └── main.py                   # - FastAPI 应用启动入口
│
├── frontend-vue/                 # 💻 前端交互展现层
│   ├── src/
│   │   ├── api/                  # - Axios 配置与 120秒超时拦截器
│   │   ├── stores/               # - Pinia 状态管理 (学习者 & 生成器)
│   │   ├── views/
│   │   │   ├── DashboardView.vue #   - 数据总览与入口面板
│   │   │   ├── LearningPathView.vue # - 个性化知识树与分支切换视图
│   │   │   └── LearningView.vue  #   - Markdown 沉浸式学习核心页面
│   │   └── App.vue
│   └── package.json
│
├── knowledge_graph/              # 🕸️ 领域知识结构
│   ├── data/
│   │   └── ml_knowledge_graph.json # - 定义了所有机器学习概念及前置关联 (DAG)
│   └── graph_builder.py          # - NetworkX 前置依赖递归核心算法
│
├── rag_engine/                   # 📚 检索增强系统
│   ├── retriever.py              # - Hybrid Retrieval (混合检索降级策略)
│   ├── vector_store.py           # - FAISS 向量封装与相似度卡点
│   └── embedding.py              # - 文本块向量化逻辑
│
└── schemas/                      # 📜 数据契约体系
    ├── agent_state_schema.py     # - 工作流流转的标准格式
    ├── learner_schema.py         # - 增强版学习者画像结构
    └── resource_schema.py        # - 约束 LLM 强制输出合法 JSON 的模版
```

---

## 三、结论与竞赛价值
AgentEdu 系统通过 **“Graph-RAG + Multi-Agent Workflow”** 这一黄金组合，从底层杜绝了通用的 ChatGPT 化问答模式，证明了我们在垂直教育领域构建具有逻辑自洽、幻觉阻断以及动态调整能力的 AI 应用的技术深度。该项目架构具备极高的横向扩展能力，可以直接复用于其他专业领域的企业级内训系统。
