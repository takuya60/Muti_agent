# AgentEdu 开发规范与环境搭建指南

> 文档版本: v1.0 | 最后更新: 2026-06-22

---

## 一、环境搭建

### 1.1 前置依赖

| 工具　　| 要求版本 | 安装方式　　　　　　　　　　　　　 |
| ---------| ----------| ------------------------------------|
| Python　| ≥ 3.10　 | [python.org](https://python.org)　 |
| Node.js | ≥ 18　　 | [nodejs.org](https://nodejs.org)　 |
| Git　　 | 最新　　 | [git-scm.com](https://git-scm.com) |

### 1.2 后端启动

```bash
# 1. 克隆仓库
git clone <repo-url>
cd agent_edu_platform

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 5. 启动后端
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

### 1.3 前端启动

```bash
cd frontend-vue
npm install
npm run dev
# 访问 http://localhost:5173
```

### 1.4 一键启动（Windows）

```bash
# 在项目根目录双击
start_agent_edu.bat
```

---

## 二、Git 分支策略

```
main              # 稳定发布分支（禁止直接 push）
├── develop       # 开发集成分支
├── feat/xxx      # 功能分支 (从 develop 拉取)
├── fix/xxx       # 修复分支
└── docs/xxx      # 文档分支
```

**工作流**:
1. 从 `develop` 创建功能分支: `git checkout -b feat/add-quiz-scoring develop`
2. 开发完成后提交 PR 到 `develop`
3. 代码审核通过后合并
4. 定期从 `develop` 合并到 `main` 发布

---

## 三、提交规范 (Conventional Commits)

```
<type>(<scope>): <description>

类型:
  feat     新功能
  fix      修复 Bug
  docs     文档变更
  style    格式调整（不影响代码逻辑）
  refactor 重构
  test     测试
  chore    构建/工具链

示例:
  feat(agent): 新增诊断 Agent 的 LLM 降级逻辑
  fix(api): 修复 /generation/stream 的 SSE 连接中断
  docs(team): 添加前后端接口文档
```

---

## 四、代码风格

### 4.1 Python

- 遵循 PEP 8
- 函数名: `snake_case`
- 类名: `PascalCase`
- 类型注解: 所有公共函数必须有类型注解
- 文档字符串: 所有公共函数必须有 docstring

### 4.2 Vue / TypeScript

- 组件名: `PascalCase`（如 `LearningView.vue`）
- 变量/函数名: `camelCase`
- CSS: 使用 `scoped` 样式，避免全局污染
- 状态管理: 统一通过 Pinia Store，禁止组件间直接传递复杂数据

---

## 五、目录职责速查

| 我是... | 我主要改这些目录 |
|--------|----------------|
| 前端开发 | `frontend-vue/src/` |
| 后端开发 | `backend/api/`, `backend/models.py`, `backend/services/` |
| Agent 开发 | `agents/`, `rag_engine/`, `knowledge_graph/` |
| 全员共同维护 | `schemas/` (数据契约), `docs/team/` (文档) |

> ⚠️ **关键原则**: 修改 `schemas/` 下的任何文件前，必须在群组通知，因为它影响所有三方开发者。
