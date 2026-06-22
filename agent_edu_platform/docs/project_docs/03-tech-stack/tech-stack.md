# AgentEdu 技术选型说明

> 文档版本: v1.0 | 最后更新: 2026-06-22

---

## 一、技术栈总览

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| 前端框架 | Vue 3 + Composition API | ^3.4 | 响应式强、生态成熟、团队熟悉度高 |
| 前端状态管理 | Pinia | ^2.1 | Vue 3 官方推荐，替代 Vuex，TS 支持好 |
| 前端构建 | Vite | ^5.0 | 极速 HMR，开发体验优于 Webpack |
| 后端框架 | FastAPI | ^0.110 | 异步高性能、自动生成 OpenAPI 文档、Pydantic 原生集成 |
| ORM | SQLAlchemy 2.0 | ^2.0 | Python 最成熟的 ORM，支持 sync/async |
| 数据库 | SQLite | 3.x | 零配置、文件级部署、足够满足竞赛演示规模 |
| Agent 编排 | LangGraph | ^0.2 | 支持有向图状态机、条件边、异步流式输出 |
| 知识图谱 | NetworkX | ^3.3 | 轻量级图算法库，支持 DAG 遍历和拓扑排序 |
| 向量检索 | FAISS | ^1.7 | Meta 开源，CPU 上即可高效检索，无需 GPU |
| 大语言模型 | DeepSeek API | Chat v3 | 中文能力强、JSON 模式稳定、性价比高 |
| 数据契约 | Pydantic v2 | ^2.7 | 类型安全、JSON Schema 自动推导、序列化性能好 |

---

## 二、关键决策记录

### 2.1 为什么选 SQLite 而不是 PostgreSQL？
- 本项目是竞赛演示项目，数据量极小（百级别）
- SQLite 零配置、无需安装数据库服务、一键启动
- 如果后续需要生产部署，只需更换 `DATABASE_URL` 即可无缝迁移到 PostgreSQL

### 2.2 为什么选 LangGraph 而不是 LangChain？
- LangChain 的 Chain 模式是线性的，无法处理"审核打回重做"的循环逻辑
- LangGraph 基于状态图 (StateGraph)，支持条件边 (conditional_edge)，天然适合我们的"生成 → 审核 → 可能打回"工作流
- LangGraph 支持 `astream`，可以将每个 Agent 节点的执行进度实时推送给前端

### 2.3 为什么选 DeepSeek 并且如何兼容 OpenAI 接口？
- **选型原因**：DeepSeek 的 `response_format: json_object` 模式在中文场景下表现稳定，API 费率极低，非常适合竞赛期间的高频测试。
- **无缝兼容 OpenAI 接口**：系统底层代码完全使用官方的 `openai` Python SDK。这意味着**系统天然兼容任何支持 OpenAI 格式的 API（包括各类中转站、GPT-3.5/4、Qwen 等）**。
- **如何切换**：由于切换成本为零，团队成员如果要使用中转站，只需修改 `.env` 文件中的 `DEEPSEEK_BASE_URL`（改为中转站地址），`DEEPSEEK_API_KEY`（改为中转站 Key），以及 `DEEPSEEK_MODEL`（如改为 `gpt-4o`）即可。唯一的前提是该模型必须支持强制输出 JSON 格式。

### 2.4 为什么前端选 Vue 3 而不是 React？
- 团队成员对 Vue 更熟悉，学习成本低
- Composition API + Pinia 的组合能力不亚于 React Hooks + Redux
- 对于竞赛项目，开发速度优先于技术前沿性
