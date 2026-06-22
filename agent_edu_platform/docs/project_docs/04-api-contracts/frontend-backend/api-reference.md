# 前端 ↔ 后端 REST/SSE 接口文档

> 文档版本: v1.0 | 最后更新: 2026-06-22
> 
> **Base URL**: `http://localhost:8001`

---

## 1. 资源生成模块 (`/generation`)

### 1.1 `POST /generation/run` — 同步生成

> 触发完整的多 Agent 流水线，阻塞等待结果。适用于调试，不推荐生产环境。

**请求体**: `LearnerProfile`

```json
{
  "learner_id": "alice_001",
  "name": "Alice",
  "background": "计算机专业大三",
  "goal": "理解逻辑回归原理并能独立调参",
  "target_algorithm": "逻辑回归",
  "target_direction": "system_recommended",
  "preferred_style": "案例驱动",
  "python_level": "data_basic",
  "math_level": "college_math",
  "ml_level": "concept",
  "practice_preference": "balanced",
  "theory_preference": "intuitive",
  "current_confusion": "",
  "project_experience": "",
  "available_time_per_week": 6,
  "test_scores": {},
  "known_skills": ["Python基础", "Numpy/Pandas"],
  "weak_points": [],
  "mastered_points": [],
  "current_level": "beginner_plus"
}
```

**响应** (200):

```json
{
  "session_id": "uuid-string",
  "generated_resources": { "...见 GeneratedResources Schema..." },
  "diagnosis": { "weak_points": [], "strengths": [], "recommended_level": "beginner_plus" },
  "evaluation": null,
  "cached": false
}
```

---

### 1.2 `POST /generation/stream` — SSE 流式生成 ⭐ 推荐

> 触发多 Agent 流水线，通过 Server-Sent Events (SSE) 实时推送每个 Agent 的执行进度。

**请求体**: 同 `POST /generation/run`

**响应**: `Content-Type: text/event-stream`

每行格式: `data: {JSON}\n\n`

**进度事件**:
```json
{"node": "diagnosis", "status": "running", "message": "🧠 画像诊断与路径规划完成..."}
{"node": "retrieval", "status": "running", "message": "📚 RAG 知识库检索完成..."}
{"node": "generation", "status": "running", "message": "✨ 核心资源生成完毕..."}
{"node": "review", "status": "running", "message": "✅ 质量审查通过！"}
{"node": "review", "status": "warning", "message": "⚠️ 审查未通过 (原因)，打回重做中..."}
{"node": "feedback", "status": "running", "message": "📝 正在生成反馈..."}
{"node": "evaluate", "status": "running", "message": "📊 评估完毕..."}
```

**最终数据事件** (含 `is_complete: true`):
```json
{
  "session_id": "uuid",
  "generated_resources": { "..." },
  "diagnosis": { "..." },
  "evaluation": { "..." },
  "cached": false,
  "is_complete": true
}
```

**缓存命中事件**:
```json
{"node": "cache", "status": "success", "message": "发现本地缓存，直接加载..."}
```

---

## 2. 学习路径模块 (`/learning-tree`)

### 2.1 `POST /learning-tree/tree` — 获取学习树

**请求体**: 学习者画像字典 (非 LearnerProfile，是原始 dict)

```json
{
  "target_algorithm": "逻辑回归",
  "target_direction": "classification",
  "python_level": "data_basic",
  "math_level": "college_math",
  "ml_level": "concept",
  "known_skills": ["Python基础"],
  "mastered_points": ["python_basics"],
  "current_level": "beginner_plus"
}
```

**响应** (200):

```json
{
  "trunk": [
    {"id": "python_basics", "name": "Python 基础", "mastered": true, "is_current": false},
    {"id": "numpy_basics", "name": "NumPy 基础", "mastered": false, "is_current": true}
  ],
  "branches": [
    {
      "id": "classification",
      "title": "分类预测",
      "description": "...",
      "recommended": true,
      "progress": 0.2,
      "locked_reason": "",
      "nodes": [
        {"id": "sigmoid_function", "name": "Sigmoid 函数", "mastered": false, "is_current": false}
      ]
    }
  ],
  "current_node": "numpy_basics",
  "current_node_name": "NumPy 基础",
  "current_branch": "trunk",
  "direction": "classification",
  "recommended_reason": "系统推荐进入分类预测分支..."
}
```

### 2.2 `POST /learning-tree/switch-branch` — 切换分支

**请求体**:
```json
{
  "learner_profile": { "...画像字典..." },
  "target_branch": "model_explanation",
  "target_algorithm": "由系统推荐"
}
```

**响应**: 同 2.1 的树结构

---

## 3. 会话管理模块 (`/sessions`)

### 3.1 `POST /sessions` — 创建会话

**请求体**:
```json
{
  "learner_id": "alice_001",
  "target_algorithm": "逻辑回归"
}
```

**响应** (200): `SessionResponse`

### 3.2 `GET /sessions/{session_id}` — 查询会话

**响应** (200): `SessionResponse` 含 `generated_resources`

### 3.3 `POST /sessions/{session_id}/messages` — 添加消息

**请求体**: `MessageCreate`
```json
{
  "role": "user",
  "content": "什么是 Sigmoid 函数？",
  "agent_name": null
}
```

### 3.4 `GET /sessions/{session_id}/messages` — 查询消息历史

**响应**: `list[MessageResponse]`

---

## 4. 交互问答模块 (`/sessions/{id}/chat`)

### 4.1 `POST /sessions/{session_id}/chat` — 同步问答

**请求体**:
```json
{ "content": "逻辑回归和线性回归有什么区别？" }
```

**响应** (200): `MessageResponse`

### 4.2 `POST /sessions/{session_id}/chat/stream` — 流式问答 ⭐ 推荐

**请求体**: 同 4.1

**响应**: `Content-Type: text/event-stream`

```
data: {"content": "逻辑回归", "done": false}
data: {"content": "与线性回归的核心区别在于", "done": false}
data: {"content": "", "done": true}
```

---

## 5. 学习者模块 (`/learners`)

### 5.1 `GET /learners/examples` — 获取示例画像列表

**响应**:
```json
[
  {"profile_name": "Alice", "learner_id": "alice_001", "name": "Alice", "goal": "学习逻辑回归"}
]
```

### 5.2 `GET /learners/{learner_id}` — 获取单个学习者详情

### 5.3 `POST /learners/validate` — 验证并保存画像

**请求体**: `LearnerProfile`

**响应**: `{"valid": true, "profile": {...}, "saved": true}`

---

## 6. 反馈决策模块 (`/feedback`)

### 6.1 `POST /feedback/decide` — 获取下一步行动建议

**请求体**:
```json
{
  "profile": { "...LearnerProfile..." },
  "quiz_accuracy": 0.75,
  "learner_feedback": "这个测试有点难"
}
```

**响应**:
```json
{
  "quiz_accuracy": 0.75,
  "learner_feedback": "这个测试有点难",
  "next_action": "生成同难度变式练习，巩固薄弱知识点",
  "resource_type": "reinforcement"
}
```

---

## 7. 评估模块 (`/evaluation`)

### 7.1 `POST /evaluation/score` — 对 WorkflowState 评分

**请求体**: `WorkflowState` (完整的工作流状态)

**响应**: 评分结果字典

---

## 通用错误响应

| 状态码 | 含义 |
|-------|------|
| 200 | 成功 |
| 400 | 请求体格式错误 |
| 404 | 会话/学习者不存在 |
| 500 | 服务端异常（通常是 LLM 调用超时） |
