# AgentEdu 产品讨论后的修改总结

> 范围：本文档只总结从“重新站在产品角度讨论”之后发生的产品决策与代码修改。  
> 目的：方便后续继续开发、交给其他 AI 接手，或用于回顾当前系统为什么变成现在的结构。  
> 注意：本文档是修改总结，不是新的实施计划。

---

## 1. 产品方向重新确认

在产品讨论之后，AgentEdu 的定位从“生成一份机器学习讲义的 demo”调整为：

> 一个面向机器学习入门与进阶学习者的 AI 教育平台，通过多 Agent 协作、RAG 知识库、知识图谱和 LLM，为不同基础的学习者生成个性化学习路径、讲义、代码练习、测验、反馈和阶段报告。

核心闭环被明确为：

```text
学情画像 → 知识图谱路径规划 → RAG 检索 → 多 Agent 协作生成 → 学习与答疑 → 测评反馈 → 路径调整
```

---

## 2. 已确定的关键产品决策

### 2.1 目标用户不再假设有 Python 基础

之前曾倾向于把目标用户定义为“有 Python 基础、想系统入门机器学习的大学生”。

用户明确指出：

> 不建议定为有 Python 基础，因为有的人可能 Python 基础薄弱，要根据用户画像具体判定。

因此目标用户调整为：

```text
希望学习机器学习的高校学生或初学者。
他们可能来自计算机、数学、商科、工科等不同背景，
在 Python 编程、数学基础、机器学习概念和项目经验上差异明显。
系统通过画像诊断决定其学习起点、学习路径、资源难度和实训任务。
```

也就是说：

```text
用户基础不是前置假设，而是画像诊断结果。
```

---

### 2.2 学习路径从单一路线改为“共同基础 + 多分支”

用户认为学习不应该完全线性，而应该：

```text
前面有共同基础
之后进入多个分支
用户可以自由选择或跳转分支
```

因此路径结构改为：

```text
共同基础
├─ Python 基础
├─ NumPy 基础
├─ Pandas 基础
├─ 机器学习任务理解
├─ 表格数据理解
├─ 数据预处理
├─ 训练/验证/测试划分
└─ sklearn 建模流程

分类预测
连续值预测
模型解释与集成
无监督探索
深度学习入门
```

产品层面不再只用算法名命名路线，例如不再只说“逻辑回归路线”，而是使用能力导向命名：

```text
分类预测
连续值预测
模型解释与集成
无监督探索
深度学习入门
```

---

### 2.3 学习形式采用“课程式 + 任务式结合”

讨论后明确：

```text
章节 = 课程式
关卡 = 小任务式
阶段成果 = 小项目式
```

也就是：

- 页面上有清晰课程结构；
- 每一关又要像一个具体学习任务；
- 阶段完成后形成报告或小项目成果。

---

### 2.4 AI 导师定位为“常驻但不主动打扰”

用户明确表示 AI 导师：

```text
不主动
```

因此导师定位是：

```text
常驻右侧，但默认安静。
用户主动提问时回答。
完成关卡、测验、切换分支时可以给必要反馈。
```

不是“话痨式 AI 老师”。

---

### 2.5 多 Agent 展示方式

用户希望多 Agent 过程：

```text
生成讲义时展示一下
详细过程放在抽屉里
用户想看再看
```

因此采用：

```text
主界面轻展示
Agent 详情抽屉展示完整协作过程
```

---

### 2.6 讲义形态

用户希望：

```text
每关 1000-1500 字
比较完整
拆成多个折叠模块
避免一屏太长
```

因此后续学习页改造方向是：

```text
为什么学这一关
核心概念
直觉解释
必要原理
项目实操中的作用
常见误区
本关小结
```

---

## 3. 新增指导文档

根据产品讨论，已新增文档：

```text
agent_edu_platform/docs/next_stage_update_guide.md
```

该文档用于交给其他 AI 或开发者继续修改代码，内容包括：

- 项目定位；
- 产品决策；
- 页面结构；
- 画像字段；
- 路径推荐逻辑；
- Dashboard；
- 学习页；
- Agent 抽屉；
- 阶段报告；
- 验证方式；
- 注意事项。

---

## 4. 后端修改总结

---

## 4.1 扩展学习者画像 Schema

修改文件：

```text
agent_edu_platform/schemas/learner_schema.py
```

原来的画像主要包含：

```text
name
goal
background
preferred_style
target_algorithm
known_skills
current_level
```

修改后新增更细粒度画像字段：

```python
python_level: 'none' | 'basic' | 'data_basic' | 'script'
math_level: 'fear_formula' | 'basic' | 'college_math' | 'derivation'
ml_level: 'none' | 'concept' | 'sklearn_demo' | 'project'
practice_preference: 'project_first' | 'balanced' | 'theory_first'
theory_preference: 'low_formula' | 'intuitive' | 'formula_ok' | 'derivation'
target_direction:
  | 'system_recommended'
  | 'common_foundation'
  | 'classification'
  | 'regression'
  | 'model_explanation'
  | 'unsupervised'
  | 'deep_learning_intro'
current_confusion: str
project_experience: str
```

目的：

```text
让系统根据 Python、数学、机器学习基础和理论/实践偏好决定学习起点与讲义风格。
```

---

## 4.2 扩展资源 Schema

修改文件：

```text
agent_edu_platform/schemas/resource_schema.py
```

新增结构包括：

```python
CommonError
LessonModule
CompletionRequirement
LearningBranch
AgentTraceStep
AgentTrace
```

`GeneratedResources` 新增字段：

```python
current_stage
current_branch
recommended_reason
lesson_modules
common_errors
completion_requirements
available_branches
agent_trace
learning_report
```

目的：

- 支持折叠式讲义模块；
- 支持代码常见错误；
- 支持完成条件；
- 支持分支进度；
- 支持 Agent 过程抽屉；
- 支持阶段报告预览。

---

## 4.3 新增路径规划模块

新增文件：

```text
agent_edu_platform/agents/path_planner.py
```

该文件负责：

```text
根据学习者画像、目标方向、已掌握节点和知识图谱，生成当前学习计划。
```

主要结构：

```python
FOUNDATION_NODES
BRANCH_NODES
BRANCH_META
TARGET_ALGORITHM_TO_DIRECTION
SKILL_NODE_MAP
PYTHON_LEVEL_MASTERED
MATH_LEVEL_MASTERED
ML_LEVEL_MASTERED
LearningPlan
build_learning_plan(...)
```

路径逻辑：

```text
1. 根据画像推断已掌握节点
2. 根据 target_direction 或 target_algorithm 解析目标分支
3. 生成完整路径：共同基础 + 目标分支
4. 找到第一个未掌握节点作为 current_node
5. 生成当前阶段、当前分支、下一关、推荐原因、分支进度
```

---

## 4.4 修改诊断 Agent

修改文件：

```text
agent_edu_platform/agents/diagnosis_agent.py
```

诊断逻辑从只看 `test_scores`，扩展为同时考虑：

```text
python_level
math_level
ml_level
practice_preference
theory_preference
current_confusion
test_scores
```

现在会根据画像输出：

```text
weak_points
strengths
recommended_level
learning_objectives
explanation_strategy
```

例如：

- Python 为 `none` 时，薄弱点包含 Python 基础、NumPy/Pandas；
- 数学为 `fear_formula` 时，策略偏少公式、多类比；
- practice_preference 为 `project_first` 时，策略偏先任务再解释。

---

## 4.5 修改检索 Agent

修改文件：

```text
agent_edu_platform/agents/retrieval_agent.py
```

检索 query 从原来的：

```text
目标算法 + 薄弱点 + 训练/测试/评估
```

扩展为：

```text
目标算法 + 目标方向关键词 + 薄弱点 + 画像字段 + 训练/测试/评估/常见错误
```

目的：

```text
让 RAG 检索更贴近当前分支和用户画像。
```

---

## 4.6 修改生成 Agent：第一轮改造

修改文件：

```text
agent_edu_platform/agents/generator_agent.py
```

第一轮改造时做了这些事：

1. 接入 `build_learning_plan(...)`；
2. 用新路径规划替代原来单一算法路径；
3. 为生成结果补齐：
   - current_stage；
   - current_branch；
   - recommended_reason；
   - available_branches；
   - lesson_modules；
   - common_errors；
   - agent_trace；
   - learning_report。

当时仍然要求 LLM 返回完整 JSON。

---

## 4.7 发现 LLM JSON 解析问题

用户反馈讲义仍像 fallback。

前端显示错误：

```text
生成模式：Fallback 模板 ｜JSON 解析失败: Expecting value: line 1 column 1 (char 0)
```

但错误中展示的原始内容前 500 字看起来已经是 LLM 生成的个性化内容，例如：

```text
Python 基础语法：从变量到控制流，构建你的第一个“手动分类器”
```

分析后判断：

```text
LLM 已经成功返回内容，
但内容不是严格合法 JSON，
后端 json.loads 失败，
于是整份 LLM 结果被丢弃并 fallback。
```

根本问题：

```text
长篇 Markdown 讲义 + 代码 + 测验 + 路径元数据全部塞进一次 JSON，解析风险太高。
```

---

## 4.8 修改生成 Agent：第二轮改造为 Markdown-only

用户决定：

```text
让 LLM 只生成 Markdown 讲义。
```

随后修改：

```text
agent_edu_platform/agents/generator_agent.py
```

新的生成逻辑：

```text
LLM 只负责生成 theory_note Markdown 讲义正文。
后端负责组装完整 GeneratedResources。
```

也就是说，LLM 不再生成：

```text
title
dataset_instruction
practice_guide
graded_quiz
learning_path
learning_path_nodes
citations
current_focus
current_stage
current_branch
agent_trace
learning_report
```

这些全部由后端确定性生成。

新增函数：

```python
_build_resources_from_markdown(...)
_dataset_instruction_for(...)
```

现在 `_llm_generation(...)` 的流程变成：

```text
1. 构造学习路径 plan
2. 构造 Markdown 讲义 prompt
3. 调用 LLM
4. 读取 response.choices[0].message.content
5. 把 content 作为 theory_note
6. 后端调用 _build_resources_from_markdown(...) 组装 GeneratedResources
```

保留 fallback：

```text
只有 API Key 缺失、LLM 调用异常、LLM 返回空内容时才 fallback。
```

---

## 4.9 修改审核 Agent 和反馈 Agent 的 Agent Trace 同步

修改文件：

```text
agent_edu_platform/agents/reviewer_agent.py
agent_edu_platform/agents/feedback_agent.py
```

目的：

```text
让 Agent 过程抽屉里的审核与反馈状态不一直停留在“等待审核”。
```

修改后：

- 审核 Agent 会同步更新 `agent_trace` 中的审核状态；
- 反馈 Agent 会同步更新 `agent_trace` 中的反馈状态。

---

## 4.10 修复 generation session 目标硬编码

修改文件：

```text
agent_edu_platform/backend/api/generation.py
```

原来创建 session 时硬编码：

```python
target_algorithm="logistic_regression"
```

修改为：

```python
target_algorithm=profile.target_algorithm
```

目的：

```text
避免无论用户选择什么方向，session 里都显示逻辑回归。
```

---

## 4.11 修改 learner 持久化逻辑

修改文件：

```text
agent_edu_platform/backend/services/learner_service.py
```

将新增画像字段写入：

```text
background summary
learning_style_model
mastered_points
current_level
knowledge_mastery
```

由于数据库表暂时没有为每个新画像字段单独建列，因此部分字段被放入：

```python
learning_style_model
```

或拼入 background summary。

---

## 5. 前端修改总结

---

## 5.1 重写画像页

修改文件：

```text
agent_edu_platform/frontend-vue/src/views/LoginView.vue
```

画像页从原来的 3 步改为 4 步：

```text
Step 1：学习目标
Step 2：基础诊断
Step 3：学习偏好
Step 4：方向与困惑
```

新增画像维度：

```text
Python 编程基础
数学基础
机器学习基础
实践 / 理论节奏
理论深度
解释风格
目标方向
当前最困惑的问题
```

用户完成画像后跳转到：

```text
/dashboard
```

而不是直接进入学习页。

---

## 5.2 新增 Dashboard 学习首页

新增文件：

```text
agent_edu_platform/frontend-vue/src/views/DashboardView.vue
```

新增路由：

```text
/dashboard
```

Dashboard 主要展示：

```text
当前学习状态
推荐关卡
推荐原因
路径进度
分支进度
最近反馈
阶段报告预览
学习画像抽屉
Agent 过程抽屉
阶段报告抽屉
```

生成资源时会显示多 Agent 生成过程：

```text
画像诊断 Agent
路径规划 Agent
知识检索 Agent
资源生成 Agent
审核纠偏 Agent
反馈规划 Agent
```

同时前端会显示：

```text
生成模式：LLM 生成
```

或：

```text
生成模式：Fallback 模板 ｜错误原因
```

---

## 5.3 新增学习路径页

新增文件：

```text
agent_edu_platform/frontend-vue/src/views/LearningPathView.vue
```

新增路由：

```text
/path
```

路径页展示：

```text
当前路线
完整节点列表
当前节点
已掌握节点
后续节点
可切换分支
分支进度
```

支持操作：

```text
标记已掌握
切换分支
```

---

## 5.4 修改路由

修改文件：

```text
agent_edu_platform/frontend-vue/src/router/index.ts
```

路由从原来的：

```text
/
/learning
```

扩展为：

```text
/
/dashboard
/path
/learning
```

---

## 5.5 重构学习页

修改文件：

```text
agent_edu_platform/frontend-vue/src/views/LearningView.vue
```

主要改动：

### 5.5.1 复用已有资源

如果从 Dashboard 进入 LearningView，且 `generationStore.currentResource` 已存在，则不再重复生成资源。

目的：

```text
避免进入学习页又触发一次 LLM 调用。
```

---

### 5.5.2 新增折叠式讲义模块

原来讲义直接显示 `theory_note`。

现在学习页会优先显示：

```text
lesson_modules
```

如果后端没有 `lesson_modules`，则 fallback 为：

```text
核心讲义
数据与任务说明
```

---

### 5.5.3 新增代码常见错误展示

代码模块新增：

```text
每步代码
解释
预期输出
常见报错与修复
本关常见错误
```

---

### 5.5.4 新增完成条件

学习页新增状态：

```ts
readConfirmed
codeConfirmed
selectedAnswers
quizSubmitted
quizScore
quizCompleted
canCompleteStep
```

完成本关条件：

```text
已阅读核心概念
已理解代码流程
测验已提交并达到要求
```

当前 MVP 中，测验得分按“是否答完”计算，而不是严格判定答案是否与参考答案完全一致。

---

### 5.5.5 新增 Agent 过程抽屉

学习页新增抽屉类型：

```text
profile
references
agent
report
```

其中 `agent` 抽屉展示后端返回的：

```text
agent_trace.steps
```

---

### 5.5.6 新增阶段报告抽屉

学习页新增阶段报告抽屉，展示：

```text
当前阶段
下一步建议
已完成节点
薄弱点
```

---

### 5.5.7 新增导师快捷提问

右侧 AI 导师栏新增快捷提问按钮：

```text
简单解释
项目例子
逐行讲代码
常见错误
```

---

### 5.5.8 聊天接口地址改为跟随 apiClient

原来聊天流地址硬编码：

```ts
http://localhost:8001/sessions/${sessionId}/chat/stream
```

修改为：

```ts
`${apiClient.defaults.baseURL}/sessions/${sessionId}/chat/stream`
```

目的：

```text
避免端口手动修改后，普通 API 和聊天流 API 不一致。
```

---

## 6. 已知当前问题

---

## 6.1 右侧 AI 导师总回复“问题与当前学习内容无关”

用户当前反馈：

```text
右侧的 AI 导师一直回复：
我是一个专业的机器学习实训导师，你的问题与当前学习的内容无关，请回到课程内容
```

这说明问题大概率出在聊天路由判断逻辑，而不是资源生成逻辑。

相关文件可能是：

```text
agent_edu_platform/agents/router_agent.py
agent_edu_platform/agents/answer_agent.py
agent_edu_platform/agents/chat_graph.py
agent_edu_platform/backend/api/chat.py
```

目前尚未修改该问题，因为用户要求先不要修改代码，只整理总结。

初步判断可能原因：

1. `router_agent` 判断过于严格；
2. 当前学习资源上下文没有被正确传给聊天 Agent；
3. 新的学习资源结构变化后，router 仍只检查旧字段；
4. 快捷提问如“简单解释”“项目例子”没有显式包含当前关卡名，被误判为 off_topic；
5. `role` 或历史消息结构不符合 router 预期。

---

## 6.2 LLM 讲义生成已改为 Markdown-only，但尚未做真实长链路验证

已经通过：

```bash
python -m py_compile agent_edu_platform/agents/generator_agent.py
npm --prefix agent_edu_platform/frontend-vue run build
```

但没有主动跑真实 LLM e2e，因为此前用户明确反感长时间卡住的后端测试。

---

## 6.3 `__pycache__` 被 py_compile 更新

运行 Python 语法检查后，git 状态中会出现：

```text
agent_edu_platform/agents/__pycache__/*.pyc
agent_edu_platform/schemas/__pycache__/*.pyc
```

这些是缓存文件，不是业务代码。

提交前建议清理或确保 `.gitignore` 忽略它们。

---

## 6.4 前端构建有 Vite/Rolldown 警告

前端构建通过，但有警告：

```text
INVALID_ANNOTATION in node_modules/@vueuse/core
Some chunks are larger than 500 kB
```

这些来自依赖和打包体积，不是当前业务逻辑错误。

---

## 7. 验证记录

多次执行并通过：

```bash
python -m py_compile agent_edu_platform/agents/generator_agent.py
```

也曾对多个后端改动文件执行：

```bash
python -m py_compile \
  agent_edu_platform/schemas/learner_schema.py \
  agent_edu_platform/schemas/resource_schema.py \
  agent_edu_platform/agents/path_planner.py \
  agent_edu_platform/agents/diagnosis_agent.py \
  agent_edu_platform/agents/retrieval_agent.py \
  agent_edu_platform/agents/generator_agent.py \
  agent_edu_platform/agents/reviewer_agent.py \
  agent_edu_platform/agents/feedback_agent.py \
  agent_edu_platform/backend/services/learner_service.py \
  agent_edu_platform/backend/api/generation.py
```

前端构建通过：

```bash
npm --prefix agent_edu_platform/frontend-vue run build
```

说明：

```text
没有主动运行真实后端 / LLM 长链路测试。
```

---

## 8. 当前重要文件清单

### 后端

```text
agent_edu_platform/schemas/learner_schema.py
agent_edu_platform/schemas/resource_schema.py
agent_edu_platform/agents/path_planner.py
agent_edu_platform/agents/diagnosis_agent.py
agent_edu_platform/agents/retrieval_agent.py
agent_edu_platform/agents/generator_agent.py
agent_edu_platform/agents/reviewer_agent.py
agent_edu_platform/agents/feedback_agent.py
agent_edu_platform/backend/api/generation.py
agent_edu_platform/backend/services/learner_service.py
```

### 前端

```text
agent_edu_platform/frontend-vue/src/views/LoginView.vue
agent_edu_platform/frontend-vue/src/views/DashboardView.vue
agent_edu_platform/frontend-vue/src/views/LearningPathView.vue
agent_edu_platform/frontend-vue/src/views/LearningView.vue
agent_edu_platform/frontend-vue/src/router/index.ts
```

### 文档

```text
agent_edu_platform/docs/next_stage_update_guide.md
agent_edu_platform/docs/product_discussion_update_summary.md
```

---

## 9. 下一步建议

由于当前用户反馈的是 AI 导师误判 off-topic，下一步应优先检查聊天链路：

```text
backend/api/chat.py
agents/chat_graph.py
agents/router_agent.py
agents/answer_agent.py
```

重点检查：

1. `router_agent` 如何判断 off_topic；
2. 当前资源上下文是否包含新字段；
3. router 是否能识别：
   - 当前关卡；
   - theory_note；
   - lesson_modules；
   - practice_guide；
   - user message；
4. 快捷提问是否需要带上当前关卡名；
5. 如果用户提问较短，如“简单解释”，是否应该默认视为当前关卡相关。

推荐产品策略：

```text
在学习页内的 AI 导师，默认用户问题与当前关卡相关。
只有明显无关的问题才拒答。
```

而不是默认严格拦截。
