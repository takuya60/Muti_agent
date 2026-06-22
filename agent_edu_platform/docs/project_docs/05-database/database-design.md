# AgentEdu 数据库设计文档

> 文档版本: v1.0 | 最后更新: 2026-06-22
>
> 数据库引擎: **SQLite 3.x** | ORM: **SQLAlchemy 2.0**
> 定义文件: `backend/models.py`

---

## 一、ER 关系图

```mermaid
erDiagram
    Learner ||--o{ Session : "1:N 学习者创建多个会话"
    Session ||--o{ Message : "1:N 会话包含多条消息"
    Learner ||--o{ QuizAttempt : "1:N 学习者答多次题"
    Session ||--o{ QuizAttempt : "1:N 会话内答多次题"

    Learner {
        string id PK "学习者 ID"
        string name "姓名"
        text background "背景描述"
        text goal "学习目标"
        string preferred_style "偏好风格"
        json test_scores "测评分数"
        json known_skills "已知技能"
        json weak_points "薄弱点"
        json mastered_points "已掌握知识点"
        string current_level "当前级别"
        json bloom_taxonomy "布鲁姆认知层级"
        json learning_style_model "学习风格雷达"
        int attention_span_minutes "专注时长"
        float frustration_index "挫败感指数"
        float engagement_score "参与度分数"
        json knowledge_mastery "节点掌握度映射"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    Session {
        string id PK "会话 ID (UUID)"
        string learner_id FK "学习者 ID"
        string target_algorithm "目标算法"
        string target_node "当前关卡节点 ID"
        string current_phase "当前阶段"
        json diagnosis_summary "诊断摘要"
        json generated_resources "生成的资源"
        json evaluation "评估快照"
        datetime created_at "创建时间"
    }

    Message {
        int id PK "自增主键"
        string session_id FK "会话 ID"
        string role "角色 (user/system/agent_event)"
        text content "消息内容"
        string agent_name "触发的 Agent 名称"
        datetime created_at "创建时间"
    }

    QuizAttempt {
        int id PK "自增主键"
        string session_id FK "会话 ID"
        string learner_id FK "学习者 ID"
        text question "题目"
        text learner_answer "学习者答案"
        text correct_answer "正确答案"
        bool is_correct "是否正确"
        string knowledge_point "对应知识点"
        datetime created_at "创建时间"
    }
```

---

## 二、表结构详解

### 2.1 `learners` — 学习者表

跨会话持久存储画像与能力雷达。

| 字段 | 类型 | 说明 | 索引 |
|------|------|------|------|
| `id` | String PK | 学习者唯一 ID | ✅ |
| `name` | String | 显示名称 | |
| `knowledge_mastery` | JSON | 知识图谱深度映射: `{node_id: mastery_score}` | |
| `frustration_index` | Float | 0.0~1.0，越高越沮丧 | |
| `engagement_score` | Float | 0.0~1.0，越高越活跃 | |

### 2.2 `sessions` — 会话表

一次完整学习交互的生命周期。

| 字段 | 类型 | 说明 | 索引 |
|------|------|------|------|
| `id` | String PK | UUID | ✅ |
| `learner_id` | String FK | 关联 learners.id | |
| `target_node` | String | 缓存 key，当前关卡节点 ID | |
| `generated_resources` | JSON | 存放完整的生成资源 | |

> **缓存策略**: 查询 `(learner_id, target_node, generated_resources IS NOT NULL)` 判断是否命中缓存。

### 2.3 `messages` — 消息表

持久化所有交互历史。

| 字段 | 类型 | 说明 |
|------|------|------|
| `session_id` | String FK | 关联 sessions.id (索引) |
| `role` | String | `user` / `system` / `agent_event` |
| `agent_name` | String | 标记是哪个 Agent 产生的消息 |

### 2.4 `quiz_attempts` — 答题记录表

用于更新画像和评测追踪。

---

## 三、迁移说明

当前使用 SQLAlchemy `Base.metadata.create_all()` 自动建表。如果修改了表结构：

1. 删除本地 `agent_edu.db` 文件
2. 重启后端服务，表会自动重建
3. 如需保留数据，请使用 Alembic 迁移工具
