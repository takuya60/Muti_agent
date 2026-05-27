# 后端数据库搭建方案 (Phase 1.2)

根据我们之前达成的“代码编写前先对齐方案”的原则，这是**阶段 1 的第 2 项任务：后端数据库搭建与重构**的详细技术实施方案。

由于我们需要评委能“零配置”跑通项目，我们坚持使用 **SQLite**，并通过 **SQLAlchemy** 进行 ORM 映射。

## 1. 依赖变更
将在 `requirements.txt` 中增加：
- `sqlalchemy>=2.0.0` (用于 ORM 和数据库操作)

## 2. 核心文件设计

### `backend/database.py` (连接引擎)
这里负责数据库连接的管理：
- 使用 SQLite 数据库文件存放在 `data/agent_edu.db`。
- 声明 `Base = declarative_base()` 作为所有数据表模型的基类。
- 提供 `get_db()` 依赖注入函数，供 FastAPI 路由在每次请求时获取独立的数据库 Session。

### `backend/models.py` (数据表模型)
我们将建立 4 张核心表：

1. **`Learner` (学习者表)**
   - 存储持久化画像：`id`, `name`, `background`, `goal`, `test_scores`, `weak_points` 等。
   - **重点**：新增 `mastered_points` (JSON数组)，用于实现跨会话的知识点掌握度累积。

2. **`Session` (学习会话表)**
   - 一次“进入系统学习某算法”的完整记录。
   - 包含：`id` (UUID), `learner_id` (外键), `target_algorithm`, `current_phase`。
   - 存放由 LangGraph 产出的**状态快照**（如 `diagnosis_summary`, `generated_resources`）。

3. **`Message` (对话消息表)**
   - 存储所有的历史对话，**不放在 LangGraph 的内存 State 中**，避免内存爆炸。
   - 包含：`session_id` (外键), `role` (user/assistant/system), `content`, `created_at`。

4. **`QuizAttempt` (答题记录表)**
   - 记录每次测试题的答题对错。
   - 包含：`session_id`, `learner_id`, `question`, `is_correct`, `knowledge_point`。用于动态更新 Learner 表的 `mastered_points`。

### `scripts/init_db.py` (初始化与迁移脚本)
由于项目之前是基于本地 JSON 文件的 (`data/learner_profiles/` 下有 `advanced.json`, `beginner.json`, `normal.json`)，这个脚本的作用是：
1. 自动创建 `agent_edu.db` 并在内部建好上述的 4 张表。
2. 自动读取那 3 个 JSON 文件，将它们的内容**无缝迁移**插入到 `Learner` 数据库表中。
3. 这样后续后端系统就可以直接从数据库读写画像，而彻底废弃本地 JSON 文件读写。

## ❓ 开放问题与确认项
> [!IMPORTANT]
> 1. 表结构中将使用 `JSON` 类型字段（SQLAlchemy 在 SQLite 中底层会映射为 Text）。这对于存储画像的列表和字典非常方便。您对表模型的设计是否有补充要求？
> 2. `init_db.py` 执行后，我们以后的逻辑将完全切换到数据库。原有 JSON 文件只作为历史备份。可以吗？

如果您觉得这个具体的数据库落地方案没有问题，请批准，我将开始为您生成对应的 3 个 Python 文件代码。
