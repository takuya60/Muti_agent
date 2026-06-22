# Agent ↔ LLM 调用规范

> 文档版本: v1.0 | 最后更新: 2026-06-22
>
> 本文档定义了所有 Agent 调用大语言模型时必须遵守的规范，包括公共调用入口、Prompt 模板和 JSON 返回格式约束。

---

## 一、公共调用入口

所有 LLM 调用**必须**通过统一网关 `agents/llm_service.py` 中的 `call_llm_json` 函数发起：

```python
def call_llm_json(
    system_prompt: str,    # 系统角色提示词
    user_prompt: str,      # 用户消息（含变量数据）
    timeout: float = 30.0, # 超时秒数
    temperature: float = 0.3,
) -> dict:
```

**行为契约**:
- 强制使用 `response_format: {"type": "json_object"}`
- 成功时返回解析后的 `dict`
- 失败时抛出异常（由调用方的 `try/except` 触发 fallback）
- **每次调用自动写入 `logs/llm_trace.jsonl`**

---

## 二、Trace 日志格式

每次调用会在 `logs/llm_trace.jsonl` 中追加一行：

```json
{
  "timestamp": "2026-06-22T10:30:00.123456",
  "latency": 2.35,
  "system_prompt": "你是一个...",
  "user_prompt": "规划数据：...",
  "raw_response": "{\"target_direction\": \"classification\", ...}",
  "error": null
}
```

---

## 三、各 Agent 的 Prompt 模板与 JSON Schema

### 3.1 诊断 Agent (`_llm_diagnosis`)

**System Prompt**:
```
你是一个教育诊断专家。根据用户画像，分析薄弱点和优势，确定推荐学习级别和解释策略。
JSON 格式要求：
{
  "weak_points": ["..."],
  "strengths": ["..."],
  "recommended_level": "beginner|beginner_plus|intermediate|advanced",
  "learning_objectives": ["..."],
  "explanation_strategy": "..."
}
```

### 3.2 路径规划 Agent (`_llm_path_decision`)

**System Prompt**:
```
你是一个智能的学习路径规划师。
根据用户画像和目标，挑选最合适的分支，推断已掌握节点，并可按需补充新的学习节点。
JSON 格式要求：
{
  "target_direction": "classification",
  "mastered_nodes": ["python_basics"],
  "recommended_reason": "你已具备...",
  "new_nodes": [
    {"id": "xgboost", "name": "XGBoost", "category": "集成学习",
     "branch": "model_explanation", "prerequisites": ["gradient_boosting"]}
  ]
}
```

**约束**:
- `target_direction` 必须是 `available_branches` 的键之一
- `mastered_nodes` 必须从已有节点列表中挑选
- `new_nodes` 最多 3 个，会被写入知识图谱 JSON 文件

### 3.3 审核 Agent (`_llm_review`)

**System Prompt**:
```
你是一个严格的教育内容审核专家。
请检查提供的教学资源是否结构完整、逻辑连贯、难度匹配，并且引用的知识库证据真实有效。
JSON 格式要求：
{
  "passed": true|false,
  "issues": ["问题1"],
  "summary": "审核通过..."
}
```

### 3.4 反馈 Agent (`_llm_feedback`)

**System Prompt**:
```
你是一个学习反馈规划师。
根据学生的测验准确率和反馈，决定下一步的教学动作和资源类型。
JSON 格式要求：
{
  "next_action": "生成降维解释...",
  "resource_type": "standard_practice|remedial_explanation|advanced_challenge|reinforcement"
}
```

---

## 四、LLM 配置 (`.env`)

```env
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

## 五、降级策略

所有 Agent 必须遵循 **"LLM 优先 + 规则兜底"** 模式：

```python
try:
    result = _llm_xxx(...)      # 先尝试 LLM
    engine = "llm"
except Exception as e:
    logger.warning(f"LLM 失败: {e}")
    result = _fallback_xxx(...) # 降级到规则
    engine = "fallback"
```

全局超时: **30 秒**。超时后自动触发降级。
