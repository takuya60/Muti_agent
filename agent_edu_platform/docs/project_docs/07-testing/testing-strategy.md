# AgentEdu 测试策略与验收标准

> 文档版本: v1.0 | 最后更新: 2026-06-22

---

## 一、测试分层策略

```
┌────────────────────────────────────────┐
│          E2E 端到端测试 (少量)           │  ← 完整流程验证
├────────────────────────────────────────┤
│          集成测试 (适量)                 │  ← API 路由 + Agent 联调
├────────────────────────────────────────┤
│          单元测试 (大量)                 │  ← 纯函数、规则引擎
└────────────────────────────────────────┘
```

---

## 二、测试文件组织

```
tests/
├── unit/                      # 单元测试
│   ├── test_path_planner.py   # 路径规划规则引擎
│   ├── test_reviewer_rules.py # 审核硬规则
│   └── test_diagnosis_fallback.py
├── integration/               # 集成测试
│   ├── test_e2e_chat.py       # 完整问答流程
│   └── test_session_api.py    # 会话 CRUD
└── manual/                    # 手动测试脚本
    └── test_stream.py         # SSE 流式验证（需启动服务端）
```

---

## 三、单元测试清单

### 3.1 路径规划器 (`agents/path_planner.py`)

| 用例 ID | 描述 | 输入 | 预期输出 |
|---------|------|------|---------|
| TP-001 | 零基础学习者推荐从 python_basics 开始 | `python_level=none` | `current_node = "python_basics"` |
| TP-002 | 有 Python 基础跳过 python_basics | `python_level=data_basic` | `current_node ≠ "python_basics"` |
| TP-003 | 指定方向为 regression 正确切换分支 | `target_direction=regression` | `direction = "regression"` |
| TP-004 | 已掌握全部基础节点后进入分支 | `mastered 含全部基础` | `current_node ∈ 分支节点` |

### 3.2 审核硬规则 (`agents/reviewer_agent.py`)

| 用例 ID | 描述 | 输入 | 预期输出 |
|---------|------|------|---------|
| TR-001 | 缺少 theory_note 字段 | resources 无 theory_note | issues 包含 "缺少必须的模块" |
| TR-002 | 代码包含 fit_transform(X_test) | practice_guide 含泄漏代码 | issues 包含 "代码存在安全隐患" |
| TR-003 | 测验题少于 3 道 | graded_quiz 仅 2 道 | issues 包含 "测验题目数量不足" |
| TR-004 | 全部合规 | 完整合法资源 | issues 为空 |

### 3.3 LLM 降级逻辑

| 用例 ID | 描述 | 模拟行为 | 预期输出 |
|---------|------|---------|---------|
| TF-001 | LLM 超时触发降级 | mock call_llm_json raise Timeout | 返回 fallback 结果 + engine="fallback" |
| TF-002 | API Key 缺失触发降级 | 设置空 DEEPSEEK_API_KEY | 返回 fallback 结果 |

---

## 四、集成测试清单

| 用例 ID | 描述 | 端点 | 验证点 |
|---------|------|------|-------|
| TI-001 | 创建会话 | POST /sessions | 返回有效 session_id |
| TI-002 | 同步生成资源 | POST /generation/run | 返回含 generated_resources 的响应 |
| TI-003 | SSE 流式生成 | POST /generation/stream | 收到 diagnosis/retrieval/generation/review 等节点事件 |
| TI-004 | 缓存命中 | 二次请求相同画像 | `cached: true` |
| TI-005 | 问答流程 | POST /sessions/{id}/chat | 返回非空 agent_response |

---

## 五、手动验收清单

### 5.1 前端 UI 验收

- [ ] 画像表单所有字段可正常填写和提交
- [ ] 生成过程中终端面板依次显示各 Agent 的执行状态
- [ ] 审核失败时终端显示具体原因
- [ ] 学习树可视化正确展示主干和分支
- [ ] 分支切换后推荐节点正确更新
- [ ] 讲义 Markdown 正确渲染（含公式、代码高亮）
- [ ] 问答功能流式输出文字

### 5.2 后端服务验收

- [ ] 后端启动无报错，无 Pydantic 序列化警告
- [ ] `logs/llm_trace.jsonl` 文件在 LLM 调用后被正确写入
- [ ] 审核失败时控制台打印 `⭕ [审核被打回]` 及具体原因清单
- [ ] LLM 不可用时所有 Agent 成功降级到规则引擎

---

## 六、运行测试

```bash
# 运行所有单元测试
python -m pytest tests/unit/ -v

# 运行集成测试（需先启动后端服务）
python -m pytest tests/integration/ -v

# 只运行某个文件
python -m pytest tests/unit/test_path_planner.py -v
```

---

## 七、性能基准

| 指标 | 目标值 | 测量方式 |
|------|-------|---------|
| 缓存命中响应时间 | ≤ 200ms | 二次请求同一画像 |
| 首次完整生成时间 | ≤ 60s | 含 LLM 调用 |
| SSE 首个事件延迟 | ≤ 3s | 从发送请求到收到第一个 SSE 事件 |
| 问答流式首 token | ≤ 2s | 从发送问题到收到第一个 chunk |
