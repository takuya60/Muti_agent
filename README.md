# 领域知识个性化生成与多智能体协同决策系统 (AgentEdu)

此仓库包含“挑战杯”竞赛的项目策划方案文档与 AgentEdu 核心系统的源代码。

AgentEdu 是一个基于大模型多智能体（Multi-Agent）与检索增强生成（RAG）技术的个性化教育实训平台。系统能够根据学习者的基础画像，动态规划知识图谱学习路径，并协同多个 Agent 实时生成深度定制化的学习讲义与实训代码。

---

## 快速开始

进入 `agent_edu_platform/` 目录，我们提供了一键启动脚本，可快速在本地运行完整的体验环境：

### 1. 环境准备
- 确保本地已安装 **Python 3.10+** 和 **Node.js (npm)**。
- 复制 `agent_edu_platform/` 目录下的 `.env.example` 文件，将其重命名为 `.env`。
- 打开 `.env` 文件，在 `DEEPSEEK_API_KEY` 处填入你自己的真实 API Key。（**注意：切勿将真实的 `.env` 文件提交到 Git 仓库中，以防 Key 泄露**）。

### 2. 一键启动
双击运行 `agent_edu_platform/start_agent_edu.bat`，脚本会自动为你：
- 检查并安装 Python 后端依赖（requirements.txt）。
- 检查并安装 Vue 前端依赖（npm install）。
- 同时启动 FastAPI 后端（端口 8001）与 Vite 前端测试服务器（端口 5173）。

### 3. 访问系统
在浏览器中打开：[http://127.0.0.1:5173](http://127.0.0.1:5173) 即可进入 AgentEdu 学习平台。

---

## 核心架构与技术亮点

本项目主要由前端 Vue 交互层、后端 FastAPI 服务层以及 LangGraph 多智能体协同层组成。

- **多智能体协同流水线 (Multi-Agent Workflow)**
  系统摒弃了单一的 Prompt 问答，构建了包含“学情诊断、路径规划、知识检索、资源生成、审核纠偏、反馈评估”在内的 6 大专业 Agent。各 Agent 像工业流水线一样各司其职，保证了生成的教学内容高质量且不偏题。
  
- **动态知识图谱 (Dynamic Knowledge Graph)**
  摒弃了传统的线性课程表，系统内置了机器学习与 Python 领域的知识图谱。根据学习者的测评水平和目标方向，实时裁剪并生成“共同基础主干 + 个性化分支”的树状学习路径。

- **RAG 检索增强生成 (Retrieval-Augmented Generation)**
  接入本地向量数据库，Agent 在生成讲义时会主动检索并引用经过严格校验的领域专家知识，有效缓解了大模型的“幻觉”问题，确保理论公式与代码片段的准确性。

---

## 目录结构说明

### 项目根目录
- **`agent_edu_platform/`**：AgentEdu 核心系统源代码（包含前后端及 Agent 逻辑）。
- **`方案 v2.md`**：项目核心策划案及比赛答辩方案 V2 版。
- **`07_领域知识个性化生成与多智能体协同决策系统研究分析.md`**：项目深入研究与底层理论分析报告。
- **`plans/`**、**`claude_review/`**：存放项目前期的构思草稿、多轮迭代记录与评审反馈。
- **`data/`**：项目所需的相关参考数据与原始资料。

### AgentEdu 系统目录 (`agent_edu_platform/`)
核心系统采用前后端分离架构，代码结构清晰，主要包含以下模块：

- **`agents/`**：多智能体大脑核心层（基于 LangGraph）
  - `workflow.py`：定义了多 Agent 的状态流转图（State Graph），控制协同执行顺序与条件分支。
  - `path_planner.py`：路径规划智能体，负责将复杂的网状知识图谱转换为适合个人的树状学习路径。
  - `generator.py` 等：各专业 Agent 的底层处理逻辑与提示词（Prompt）封装。

- **`backend/`**：API 服务与持久化层（FastAPI + SQLite）
  - `main.py`：后端服务入口与路由总线。
  - `api/`： RESTful 接口层（如 `generation.py` 负责调度大模型生成，`learning_tree.py` 负责路径切换）。
  - `models.py`：数据库表结构定义（包含深度学习者画像 Learner 与会话缓存 Session）。

- **`frontend-vue/`**：用户交互展示层（Vue3 + Pinia + Vite）
  - `src/views/`：核心视图页面（包含 `DashboardView.vue` 首页看板、`LearningPathView.vue` 树状可视化路径、`LearningView.vue` 沉浸式学习流）。
  - `src/stores/`：全局状态管理（处理本地缓存与大模型流式状态）。
  - `src/components/`：高度解耦的 UI 交互组件库。

- **`knowledge_graph/`**：底层知识中枢层
  - `graph_builder.py`：基于 NetworkX 构建的领域有向无环图（DAG），提供前置知识依赖判定与智能下一关推荐算法。

- **`schemas/`**：跨系统数据契约层
  - 集中存放 Pydantic 模型，严格约束前端请求、后端流转以及各个 Agent 之间互相通信的 JSON 数据结构，避免了大模型输出格式不可控的问题。
