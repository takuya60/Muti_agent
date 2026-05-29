# AgentEdu 下一阶段代码修改指导文档

> 用途：这份文档用于交给其他 AI 或开发者继续修改代码。  
> 项目目录大致为：`E:/挑战杯/agent_edu_platform`  
> 当前目标：把项目从“生成一次学习资源的 demo”升级为“多 Agent 驱动的个性化机器学习实训平台”。

---

## 1. 项目总体定位

### 1.1 产品定位

AgentEdu 应定位为：

> 一个面向机器学习入门与进阶学习者的 AI 教育平台，通过多 Agent 协作、RAG 知识库、知识图谱和 LLM，为不同基础的学习者生成个性化学习路径、讲义、代码练习、测验、反馈和阶段报告。

它不是单纯的 ChatGPT 聊天助手，也不是普通网课平台，而是一个闭环学习系统：

```text
学情画像 → 知识图谱路径规划 → RAG 检索 → 多 Agent 协作生成 → 学习与答疑 → 测评反馈 → 路径调整
```

### 1.2 核心比赛叙事

项目需要重点突出：

1. **多 Agent 系统**
   - 不是一个 LLM 直接生成所有内容；
   - 而是多个 Agent 分工协作：
     - 画像诊断 Agent；
     - 路径规划 Agent；
     - 知识检索 Agent；
     - 资源生成 Agent；
     - 内容审核 Agent；
     - 反馈规划 Agent。

2. **RAG + 知识库**
   - 讲义、代码、测验不是凭空生成；
   - 应结合本地机器学习知识库切片；
   - 内容需要有引用来源。

3. **知识图谱**
   - 学习路径不是固定线性路线；
   - 应该有共同基础和多个分支；
   - 系统能根据用户基础推荐起点和下一步。

4. **个性化学习闭环**
   - 不同用户的 Python 基础、数学基础、机器学习基础、理论/实践偏好不同；
   - 系统应生成不同路径、不同讲义深度、不同练习和不同测验。

---

## 2. 当前项目已有能力

### 2.1 前端

技术栈：

```text
Vue 3
Vite
TypeScript
Pinia
```

已有页面大致包括：

```text
frontend-vue/src/views/LoginView.vue
frontend-vue/src/views/LearningView.vue
```

已有能力：

- 画像填写；
- 学习资源生成；
- 右侧 AI 导师对话；
- Markdown 渲染；
- KaTeX 公式渲染；
- 正常色调 / 夜间模式；
- 当前关卡完成并进入下一关；
- 基础学习路径展示。

### 2.2 后端

技术栈：

```text
FastAPI
SQLAlchemy
SQLite
Pydantic
LangGraph-like workflow
OpenAI-compatible DeepSeek client
```

已有能力：

- 学习者画像；
- 多 Agent 工作流雏形；
- RAG 检索；
- 知识图谱读取；
- LLM 生成讲义；
- SSE 聊天接口。

重要接口可能包括：

```text
/generation/run
/sessions/{session_id}/chat/stream
```

不要随意破坏现有接口，除非同步修改前端调用。

### 2.3 知识库

当前知识库已经扩展到较多机器学习知识切片，位于：

```text
agent_edu_platform/data/knowledge_base/processed/
```

知识图谱位于：

```text
agent_edu_platform/knowledge_graph/data/ml_knowledge_graph.json
```

当前已覆盖：

- Python / NumPy / Pandas；
- 机器学习任务理解；
- 数据预处理；
- 特征工程；
- 训练/验证/测试划分；
- sklearn 流程；
- 线性回归；
- 逻辑回归；
- 决策树；
- 随机森林；
- GBDT；
- KNN；
- 模型评估；
- PCA；
- KMeans；
- DBSCAN；
- 神经网络；
- Keras 入门等。

---

## 3. 重要开发约束

### 3.1 不要泄露密钥

项目中曾经出现过 `.env` 暴露 API Key 的情况。

要求：

```text
不要读取、打印、提交、复述 .env 中的密钥。
不要把 API Key 写死进代码。
不要提交 .env。
```

如果需要环境变量，使用：

```python
os.getenv("DEEPSEEK_API_KEY")
```

或已有配置方式。

### 3.2 不要默认运行长链路测试

之前后端 e2e 测试因为真实 LLM / HuggingFace 下载 / 向量模型加载等原因卡住过。

要求：

```text
不要默认运行长时间 LLM 测试。
不要默认运行完整 e2e 测试。
不要默认触发 HuggingFace 大模型下载。
```

建议验证方式：

```text
1. 前端 npm run build
2. Python 语法检查
3. 轻量单元测试
4. 手动运行应用验证
```

### 3.3 不要直接提交 git

除非用户明确要求：

```text
不要 git commit
不要 git push
不要 git reset --hard
不要删除用户未确认的文件
```

### 3.4 尊重已有端口修改

用户已经手动修改过端口。

要求：

```text
不要把端口强行改回旧值。
不要硬编码新的端口。
如需修改 API base URL，应检查现有配置。
```

---

## 4. 产品决策汇总

### 4.1 目标用户

不要把目标用户限定为：

```text
有 Python 基础的大学生
```

因为用户可能 Python 基础薄弱。

更准确的目标用户是：

> 希望学习机器学习的高校学生或初学者，他们可能来自计算机、数学、商科、工科等不同背景，在 Python 编程、数学基础、机器学习概念和项目经验上差异明显。系统通过画像诊断决定其学习起点、学习路径、资源难度和实训任务。

也就是说：

```text
用户基础不是前置假设，而是画像诊断结果。
```

### 4.2 用户痛点

核心痛点是：

```text
网上资料太多，但路线混乱。
不知道从哪里开始学。
学了很多零散知识，但不知道下一步该学什么。
```

因此产品必须重点回答：

```text
我现在在哪？
我下一步学什么？
为什么我应该学这个？
我学完后能做什么？
```

### 4.3 学习路径结构

不要做完全线性的路径。

应该设计成：

```text
共同基础 + 多条分支
```

推荐结构：

```text
共同基础
├─ Python 基础
├─ NumPy 基础
├─ Pandas 基础
├─ 机器学习任务理解
├─ 表格数据理解
├─ 数据预处理
├─ 训练/验证/测试划分
├─ sklearn 建模流程
└─ 基础评估指标

分类预测分支
├─ 逻辑回归
├─ KNN
├─ 决策树
├─ 混淆矩阵
├─ Precision / Recall / F1
└─ ROC-AUC / PR 曲线

连续值预测分支
├─ 线性回归
├─ 多项式回归
├─ Ridge / Lasso
├─ MAE / MSE / RMSE / R²
└─ 回归任务实战

模型解释与集成分支
├─ 决策树
├─ 剪枝
├─ 随机森林
├─ GBDT
└─ 特征重要性

无监督探索分支
├─ 特征缩放
├─ PCA
├─ KMeans
├─ DBSCAN
└─ 聚类评估

深度学习入门分支
├─ 神经网络直觉
├─ 前向传播
├─ 反向传播
├─ 激活函数
├─ Keras Sequential
└─ 过拟合与早停
```

### 4.4 分支命名

产品层面不要只用算法名命名。

不推荐：

```text
逻辑回归路线
线性回归路线
决策树路线
```

推荐：

```text
分类预测
连续值预测
模型解释与集成
无监督探索
深度学习入门
```

算法是分支中的工具，不是唯一终点。

### 4.5 学习形式

用户希望：

```text
课程式 + 任务式结合
```

推荐落地方式：

```text
章节 = 课程式
关卡 = 小任务式
阶段成果 = 小项目式
```

例如：

```text
章节：共同基础
关卡：处理缺失值
任务：让一份表格数据可以被模型训练使用

章节：分类预测
关卡：训练逻辑回归
任务：预测学生是否存在学习风险

阶段成果：完成一个小型机器学习项目
```

### 4.6 AI 导师定位

AI 导师应该：

```text
常驻，但不主动打扰。
```

也就是说：

- 右侧导师栏可以一直存在；
- 用户不问时，不要频繁主动发言；
- 可以提供快捷提问；
- 在用户完成关卡、测验、切换分支时给必要反馈；
- 不要做成话痨式 AI。

定位：

```text
安静、专业、随时可问的学习助教。
```

### 4.7 多 Agent 展示方式

用户希望：

```text
生成讲义时展示一下多 Agent 协作过程。
详细过程放在抽屉里，用户想看再看。
```

不要把主界面做成 Agent 日志大屏。

推荐主界面展示：

```text
正在生成你的学习资源...

✓ 画像诊断 Agent：分析你的基础
✓ 路径规划 Agent：匹配知识图谱节点
✓ 检索 Agent：查找相关知识片段
✓ 生成 Agent：生成讲义、代码和测验
✓ 审核 Agent：检查难度、结构和引用
✓ 反馈 Agent：规划下一步

[查看 Agent 协作详情]
```

点击后在抽屉中显示详细过程。

### 4.8 讲义长度与结构

用户希望：

```text
每关 1000-1500 字，比较完整。
拆成多个折叠模块，避免一屏太长。
```

不要生成极短模板化讲义。

推荐每关结构：

```text
1. 为什么学这一关
2. 核心概念
3. 直觉解释
4. 必要公式 / 原理
5. 代码实操
6. 常见错误
7. 小结
8. 小测验
```

### 4.9 代码实操

用户希望：

```text
分步骤解释每段代码。
给常见报错和修复建议。
```

代码模块不要只给一个代码块。

推荐结构：

```text
步骤 1：导入库
代码
解释

步骤 2：读取数据
代码
解释

步骤 3：处理缺失值
代码
解释

常见错误：
- KeyError: 列名不存在
- ValueError: 输入包含 NaN
- 数据泄露：在划分前对全量数据 fit
```

### 4.10 完成关卡条件

用户希望：

```text
多种条件结合。
```

MVP 可以先做成：

```text
阅读确认 + 代码理解确认 + 小测验 + 用户点击完成
```

前端表现：

```text
□ 我已阅读核心概念
□ 我理解了本关代码流程
□ 我完成了小测验
[完成本关]
```

未来再加入：

```text
AI 判断
代码运行结果
学习时间
错题分析
```

### 4.11 页面结构

用户希望 MVP 至少包含：

```text
登录/画像页
学习首页/仪表盘
学习路径页
阶段报告页
个人画像页
设置页
Agent 过程详情页
```

其中当前阶段最重要的是：

```text
画像页
学习首页
当前关卡学习页
学习路径页
阶段报告
```

### 4.12 学习页布局

用户希望：

```text
主内容 + 右侧常驻 AI 导师
```

推荐布局：

```text
左/顶部：路径入口、当前阶段
中间：当前关卡内容
右侧：AI 导师
抽屉：画像、Agent 过程、阶段报告、设置
```

### 4.13 抽屉

用户希望有：

```text
学习画像抽屉
Agent 生成过程抽屉
阶段报告抽屉
设置抽屉
```

注意：用户提到了两次学习画像抽屉，说明这个模块比较重要。

### 4.14 暂时可以砍掉的内容

这些暂时不要做：

```text
真实用户注册登录
在线运行代码
复杂知识图谱可视化
教师端
班级管理
多课程支持
移动端深度适配
商业化/支付
完整后台管理系统
长期历史学习记录
```

---

## 5. 下一阶段总体目标

下一阶段代码修改目标：

```text
把 AgentEdu 从“画像后生成一份讲义”升级为“可诊断、可规划、可学习、可反馈、可调整路径”的个性化机器学习实训平台。
```

优先级最高的三个改造：

```text
1. 重构画像字段
2. 重构路径推荐逻辑
3. 新增学习首页 / Dashboard
```

然后再做：

```text
4. 学习路径页
5. 关卡页模块化
6. Agent 过程抽屉
7. 阶段报告
8. UI 细节优化
```

---

## 6. 阶段一：重构画像系统

### 6.1 当前问题

当前画像页大致包含：

```text
名字
目标
背景
学习风格
阶段目标
已掌握技能
综合水平
```

问题：

```text
“综合水平”太粗糙。
“背景”不能准确决定学习路径。
Python 基础、数学基础、ML 基础没有拆开。
理论偏好和实践偏好不够清晰。
```

### 6.2 新画像字段

建议画像页收集以下信息。

#### 基础信息

```ts
name: string
learning_goal: string
```

学习目标可选：

```text
系统入门机器学习
完成一个小项目
补齐课程/竞赛基础
理解算法原理
提升代码实战能力
只是随便看看
```

#### Python 编程基础

字段：

```ts
python_level: 'none' | 'basic' | 'data_basic' | 'script'
```

选项：

```text
几乎没写过 Python
会变量、循环、函数等基础语法
会 NumPy / Pandas 基础操作
能独立完成数据处理脚本
```

#### 数学基础

字段：

```ts
math_level: 'fear_formula' | 'basic' | 'college_math' | 'derivation'
```

选项：

```text
害怕公式，希望少一点推导
能理解基础函数和概率概念
学过线性代数 / 概率论
能接受较完整的公式推导
```

#### 机器学习基础

字段：

```ts
ml_level: 'none' | 'concept' | 'sklearn_demo' | 'project'
```

选项：

```text
完全没接触过
看过概念，但没写过代码
跑过 sklearn 示例
做过简单项目
```

#### 项目实践偏好

字段：

```ts
practice_preference: 'project_first' | 'balanced' | 'theory_first'
```

选项：

```text
先做项目，再解释原理
理论和实践平衡
先理解原理，再写代码
```

#### 理论深度偏好

字段：

```ts
theory_preference: 'low_formula' | 'intuitive' | 'formula_ok' | 'derivation'
```

选项：

```text
尽量少公式
多用直觉和类比
可以接受必要公式
希望看到完整推导
```

#### 目标方向

字段：

```ts
target_direction:
  | 'system_recommended'
  | 'common_foundation'
  | 'classification'
  | 'regression'
  | 'model_explanation'
  | 'unsupervised'
  | 'deep_learning_intro'
```

选项：

```text
由系统推荐
先打共同基础
分类预测
连续值预测
模型解释与集成
无监督探索
深度学习入门
```

#### 当前困惑，可选

字段：

```ts
current_confusion: string
```

例如：

```text
不知道从哪里开始
看得懂教程但不会写代码
公式看不懂
不知道模型指标是什么意思
学了很多但串不起来
```

### 6.3 前端文件建议

主要修改：

```text
frontend-vue/src/views/LoginView.vue
frontend-vue/src/stores/learner.ts
frontend-vue/src/types/*
```

如果当前没有统一 types 文件，可以考虑新增：

```text
frontend-vue/src/types/learner.ts
```

但不要为了抽象而过度新增文件。

### 6.4 后端文件建议

可能需要修改：

```text
schemas/learner_schema.py
backend/main.py
agents/diagnosis_agent.py
agents/generator_agent.py
agents/workflow.py
```

具体以当前项目结构为准。

### 6.5 画像诊断输出

后端不应该只保存用户填写项，还应该形成诊断结果：

```json
{
  "python_level": "none",
  "math_level": "basic",
  "ml_level": "none",
  "practice_preference": "project_first",
  "theory_preference": "low_formula",
  "target_direction": "system_recommended",
  "weak_points": [
    "python_basics",
    "pandas_basics",
    "ml_task_framing"
  ],
  "recommended_start_node": "python_basics",
  "recommended_branch": "common_foundation"
}
```

---

## 7. 阶段二：重构学习路径推荐逻辑

### 7.1 当前问题

当前路径容易像：

```text
用户选择某个算法 → 系统给出该算法路线
```

这会导致产品显得像算法菜单，而不是个性化学习系统。

### 7.2 新逻辑

路径推荐应根据：

```text
Python 基础
数学基础
机器学习基础
理论/实践偏好
目标方向
已完成节点
已掌握节点
用户手动跳过节点
```

共同决定。

### 7.3 推荐规则示例

#### Python 很弱

```text
python_level = none
```

推荐起点：

```text
python_basics
```

后续：

```text
numpy_basics → pandas_basics → tabular_data_understanding
```

#### Python 尚可，但 ML 为零

```text
python_level = basic 或 data_basic
ml_level = none
```

推荐起点：

```text
ml_task_framing
```

后续：

```text
tabular_data_understanding → train_validation_test_split → sklearn_workflow
```

#### 数学弱，偏实践

```text
math_level = fear_formula
practice_preference = project_first
```

讲义策略：

```text
少公式
多类比
多案例
代码解释细
测验偏理解和应用
```

#### 数学强，偏理论

```text
math_level = derivation
theory_preference = derivation
```

讲义策略：

```text
可以加入公式
解释损失函数
加入推导
测验可提高难度
```

#### 用户选择深度学习入门，但基础不足

系统应该允许切换，但提示：

```text
你可以进入深度学习入门分支。
不过系统检测到你还没有完成“特征缩放”和“训练/验证划分”，这些会影响后续理解。
建议先补齐这两个节点。
```

### 7.4 建议数据结构

可以在后端定义学习节点：

```python
class LearningNode(BaseModel):
    id: str
    title: str
    stage: str
    branch: str
    prerequisites: list[str] = []
    difficulty: str = "beginner"
    estimated_minutes: int = 20
    is_required: bool = True
    can_skip: bool = True
```

分支：

```python
class LearningBranch(BaseModel):
    id: str
    title: str
    description: str
    nodes: list[str]
    recommended: bool = False
    locked_reason: str = ""
```

### 7.5 路径推荐输出

`GeneratedResources` 或相关 response 中建议包含：

```json
{
  "current_focus": "Python 基础语法",
  "current_focus_id": "python_basics",
  "current_stage": "共同基础",
  "current_branch": "common_foundation",
  "recommended_reason": "你的 Python 基础较弱，建议先补齐基础语法。",
  "learning_path_nodes": ["python_basics", "numpy_basics", "pandas_basics"],
  "available_branches": [
    {
      "id": "classification",
      "title": "分类预测",
      "progress": 0.2,
      "recommended": true
    }
  ],
  "next_focus": "NumPy 基础"
}
```

---

## 8. 阶段三：新增学习首页 / Dashboard

### 8.1 目标

当前用户登录后不应只看到一个学习页。  
需要一个学习首页回答：

```text
我现在在哪？
我下一步学什么？
我为什么学这个？
我有哪些分支可以选？
```

### 8.2 推荐路由

可以新增：

```text
/dashboard
```

也可以调整为：

```text
/login
/dashboard
/learning
/path
/report
/settings
```

如果当前路由较简单，至少新增：

```text
frontend-vue/src/views/DashboardView.vue
```

并修改 router。

### 8.3 Dashboard 模块

#### 模块一：当前状态

```text
当前阶段：共同基础
当前关卡：Python 基础语法
推荐原因：你填写的 Python 基础为“几乎没写过”
预计时间：20 分钟
```

#### 模块二：继续学习

按钮：

```text
继续当前关卡
```

点击进入：

```text
/learning
```

#### 模块三：分支进度

卡片：

```text
共同基础：20%
分类预测：未开始
连续值预测：未开始
无监督探索：未开始
深度学习入门：未开始
```

每个卡片显示：

```text
是否推荐
前置知识是否满足
完成度
```

#### 模块四：最近反馈

```text
最近完成：机器学习任务理解
薄弱点：Pandas 数据处理
下一步建议：继续学习 Pandas 基础
```

#### 模块五：Agent 过程入口

```text
查看最近一次 Agent 协作过程
```

### 8.4 Dashboard 设计风格

保持正常教育产品风格：

```text
清爽
可信
像学习平台
少量玻璃卡片
合理阴影
不要过度 AI cyber 风
```

---

## 9. 阶段四：新增或重构学习路径页

### 9.1 目标

路径页要展示：

```text
共同基础 + 多分支
```

并允许用户手动调整。

### 9.2 路径页模块

建议新增：

```text
frontend-vue/src/views/LearningPathView.vue
```

或者在现有学习页中做路径抽屉，但独立页面更清晰。

### 9.3 页面内容

#### 顶部

```text
你的学习路径
系统根据你的画像推荐从“Python 基础”开始。
你可以切换分支，也可以标记已掌握。
```

#### 共同基础区

展示节点列表：

```text
Python 基础
NumPy 基础
Pandas 基础
机器学习任务理解
表格数据理解
数据预处理
训练/验证/测试划分
sklearn 流程
```

状态：

```text
已完成
当前
推荐
未开始
可跳过
```

#### 分支区

分支卡片：

```text
分类预测
连续值预测
模型解释与集成
无监督探索
深度学习入门
```

每张卡片显示：

```text
简介
进度
推荐程度
前置知识提示
进入分支按钮
```

### 9.4 用户操作

至少支持三个操作：

```text
标记已掌握
切换分支
查看前置知识
```

P1 可支持：

```text
太简单
太难
稍后再学
```

---

## 10. 阶段五：重构当前关卡学习页

### 10.1 当前目标

把当前关卡页升级成真正的学习工作台。

推荐布局：

```text
主内容 + 右侧常驻导师
```

### 10.2 顶部关卡信息

主内容顶部显示：

```text
当前关卡：缺失值处理
所属阶段：共同基础
推荐原因：你选择项目实践路线，且数据处理基础较弱
预计时间：20 分钟
完成后解锁：类别变量编码
```

### 10.3 讲义模块

不要一整段长文本直接铺开。  
拆成折叠模块：

```text
为什么学这一关
核心概念
直觉解释
必要公式 / 原理
代码实操
常见错误
小结
小测验
```

### 10.4 后端资源结构建议

当前 `GeneratedResources` 中可能只有：

```python
theory_note: str
dataset_instruction: str
practice_guide: list[CodeStep]
graded_quiz: list[QuizItem]
```

建议逐步扩展为：

```python
class LessonModule(BaseModel):
    title: str
    type: str
    content: str
    default_open: bool = False

class CommonError(BaseModel):
    error: str
    cause: str
    fix: str

class CompletionRequirement(BaseModel):
    read_required: bool = True
    code_required: bool = True
    quiz_required: bool = True
    min_quiz_score: int = 60
```

`GeneratedResources` 可以增加：

```python
why_learn: str = ""
lesson_modules: list[LessonModule] = []
common_errors: list[CommonError] = []
completion_requirements: CompletionRequirement
recommended_reason: str = ""
current_stage: str = ""
current_branch: str = ""
```

注意：为了避免破坏现有前端，可以保留旧字段，同时新增字段。

### 10.5 前端兼容策略

如果后端暂时还没有 `lesson_modules`，前端可以 fallback：

```ts
const modules = computed(() => {
  if (resource.lesson_modules?.length) return resource.lesson_modules

  return [
    {
      title: '核心讲义',
      type: 'theory',
      content: resource.theory_note,
      default_open: true
    },
    {
      title: '数据与任务说明',
      type: 'dataset',
      content: resource.dataset_instruction,
      default_open: false
    }
  ]
})
```

这样不会一下子破坏已有功能。

---

## 11. 阶段六：完善代码练习模块

### 11.1 目标

代码练习不能只是代码块。

应该展示：

```text
步骤
代码
解释
常见问题
```

### 11.2 建议结构

后端 `CodeStep` 可扩展：

```python
class CodeStep(BaseModel):
    title: str
    code: str
    explanation: str
    expected_output: str = ""
    common_errors: list[CommonError] = []
```

如果已有 `CodeStep` 字段不同，尽量做兼容扩展。

### 11.3 前端展示

每个代码步骤：

```text
步骤 1：导入库
[代码块]
解释：
这一步导入 pandas 和 sklearn 中的数据处理工具。

常见错误：
- ModuleNotFoundError: 没安装 sklearn
  解决：pip install scikit-learn
```

---

## 12. 阶段七：测验与完成条件

### 12.1 当前目标

完成关卡不能只靠一个按钮。  
但 MVP 也不要做太复杂。

### 12.2 MVP 完成条件

前端维护三个状态：

```ts
readConfirmed: boolean
codeConfirmed: boolean
quizCompleted: boolean
quizScore: number
```

完成按钮启用条件：

```ts
readConfirmed && codeConfirmed && quizCompleted && quizScore >= minQuizScore
```

如果暂时不做真实测验评分，可以先做：

```text
用户选择答案后计算分数。
```

### 12.3 完成后行为

完成后：

```text
1. 更新 mastered_points
2. 更新 knowledge_mastery
3. 记录 quiz_score
4. 请求后端重新推荐下一关
5. 更新 dashboard/path/learning 页面状态
```

### 12.4 后端进度结构建议

```python
class LearningProgress(BaseModel):
    learner_id: str
    completed_nodes: list[str] = []
    skipped_nodes: list[str] = []
    current_node: str = ""
    current_branch: str = ""
    quiz_scores: dict[str, float] = {}
    mastery: dict[str, float] = {}
    difficulty_feedback: dict[str, str] = {}
```

如果当前系统没有持久化完整进度，MVP 可先存在 Pinia / SQLite 简化表中。

---

## 13. 阶段八：Agent 协作过程展示

### 13.1 生成中轻展示

当资源生成时，不要只显示 spinner。

展示：

```text
正在生成你的学习资源

✓ 画像诊断 Agent：分析学习基础
✓ 路径规划 Agent：匹配知识图谱节点
✓ 检索 Agent：查找知识库片段
✓ 生成 Agent：生成讲义、代码和测验
✓ 审核 Agent：检查难度、结构和引用
✓ 反馈 Agent：规划下一步
```

如果后端不能真实流式返回每一步，也可以前端先做阶段化 loading，但文案要和真实流程一致。

### 13.2 Agent 详情抽屉

新增抽屉：

```text
AgentProcessDrawer
```

展示：

```text
诊断 Agent
- Python 基础：薄弱
- 数学基础：基础
- 推荐起点：Python 基础

路径规划 Agent
- 当前节点：python_basics
- 当前阶段：共同基础
- 后续节点：numpy_basics, pandas_basics

检索 Agent
- 命中知识片段：
  - python_basics.md
  - pandas_basics.md

生成 Agent
- 生成内容：
  - 讲义模块
  - 代码练习
  - 小测验

审核 Agent
- 难度匹配：通过
- 引用完整：通过
- 结构完整：通过
```

### 13.3 后端 Agent Trace

建议在返回资源中加入：

```python
class AgentTraceStep(BaseModel):
    agent: str
    title: str
    status: str
    summary: str
    details: list[str] = []

class AgentTrace(BaseModel):
    steps: list[AgentTraceStep] = []
```

`GeneratedResources` 增加：

```python
agent_trace: AgentTrace | None = None
```

---

## 14. 阶段九：阶段报告

### 14.1 目标

用户完成一个阶段后，生成学习报告。

这对比赛展示非常重要，因为它体现：

```text
反馈闭环
学习结果沉淀
个性化调整
```

### 14.2 报告内容

阶段报告应包括：

```text
1. 本阶段学习总结
2. 已完成关卡
3. 掌握较好的知识点
4. 仍然薄弱的知识点
5. 测验表现
6. AI 导师反馈
7. 下一阶段推荐路线
8. 可复制的学习总结
```

### 14.3 数据结构建议

```python
class LearningReport(BaseModel):
    learner_id: str
    stage: str
    completed_nodes: list[str]
    strengths: list[str]
    weak_points: list[str]
    quiz_summary: str
    tutor_feedback: str
    next_recommendation: str
    generated_at: str
```

### 14.4 前端展示

可以新增：

```text
frontend-vue/src/views/ReportView.vue
```

或用抽屉：

```text
StageReportDrawer
```

MVP 可以先做抽屉，后续再独立页面。

---

## 15. 阶段十：右侧 AI 导师优化

### 15.1 保持常驻

右侧导师栏继续常驻。

### 15.2 不主动打扰

默认不要自动频繁发送消息。

可以在特定事件后发送系统提示：

```text
你已完成本关，我已经根据你的测验结果更新了掌握度。
```

但不要不断主动提问。

### 15.3 增加快捷提问

推荐按钮：

```text
用更简单的话解释
给我一个例子
逐行解释代码
我想看公式版解释
这个知识点常见错误是什么
帮我总结本关
```

点击后填入或直接发送对应问题。

### 15.4 聊天上下文

聊天请求中应携带：

```text
当前关卡
当前讲义
用户画像
当前代码练习
学习路径
```

如果已有后端 session 机制，应确保 session 中保存这些上下文。

---

## 16. 阶段十一：知识库和知识图谱结构化

### 16.1 当前问题

知识库已经扩展，但还可以增强 metadata，方便路径推荐和检索。

### 16.2 知识切片 metadata

每个 markdown 文件可考虑增加 frontmatter：

```yaml
---
id: missing_value_handling
title: 缺失值处理
stage: 共同基础
branch: 数据预处理
difficulty: beginner
prerequisites:
  - tabular_data_understanding
related:
  - categorical_encoding
  - sklearn_workflow
---
```

如果短期不想改所有文件，也可以先在后端维护一个节点 metadata 字典。

### 16.3 知识图谱节点属性

`ml_knowledge_graph.json` 中节点建议包含：

```json
{
  "id": "missing_value_handling",
  "name": "缺失值处理",
  "stage": "共同基础",
  "branch": "数据预处理",
  "difficulty": "beginner",
  "estimated_minutes": 20,
  "is_required": true,
  "can_skip": true
}
```

---

## 17. 建议修改文件清单

### 17.1 前端

重点文件：

```text
frontend-vue/src/views/LoginView.vue
frontend-vue/src/views/LearningView.vue
frontend-vue/src/stores/learner.ts
frontend-vue/src/stores/generation.ts
frontend-vue/src/router/index.ts
frontend-vue/src/api/*
```

建议新增：

```text
frontend-vue/src/views/DashboardView.vue
frontend-vue/src/views/LearningPathView.vue
frontend-vue/src/views/ReportView.vue

frontend-vue/src/components/AgentProcessDrawer.vue
frontend-vue/src/components/LearnerProfileDrawer.vue
frontend-vue/src/components/StageReportDrawer.vue
frontend-vue/src/components/SettingsDrawer.vue

frontend-vue/src/components/LessonModuleList.vue
frontend-vue/src/components/CodePracticePanel.vue
frontend-vue/src/components/QuizPanel.vue
frontend-vue/src/components/CompletionChecklist.vue
```

如果项目较小，不要过度拆组件，可以先在 `LearningView.vue` 内实现，再逐步抽离。

### 17.2 后端

重点文件：

```text
schemas/learner_schema.py
schemas/resource_schema.py
agents/diagnosis_agent.py
agents/generator_agent.py
agents/retrieval_agent.py
agents/reviewer_agent.py
agents/feedback_agent.py
agents/workflow.py
backend/main.py
knowledge_graph/data/ml_knowledge_graph.json
rag_engine/retriever.py
```

可能新增：

```text
schemas/progress_schema.py
schemas/report_schema.py
services/path_planner.py
services/report_service.py
```

如果当前项目结构简单，也可以先不要新增太多 service 文件，避免架构膨胀。

---

## 18. 推荐实施顺序

### 第一步：数据模型先行

先更新：

```text
LearnerProfile
GeneratedResources
LearningProgress
AgentTrace
```

原因：

```text
前端和 Agent 都依赖数据结构。
```

### 第二步：画像页重构

把画像页改为真正的基础诊断：

```text
Python 基础
数学基础
ML 基础
理论/实践偏好
目标方向
当前困惑
```

### 第三步：路径推荐逻辑

根据画像决定：

```text
当前节点
当前阶段
推荐分支
下一节点
推荐原因
```

### 第四步：新增 Dashboard

登录后进入 Dashboard。

Dashboard 显示：

```text
当前状态
推荐下一关
分支进度
最近反馈
继续学习入口
```

### 第五步：重构 LearningView

把当前关卡页改成：

```text
折叠讲义
代码步骤
常见错误
测验
完成条件
右侧导师
```

### 第六步：Agent 过程抽屉

先做前端展示结构。

后端如果已有 trace，则接真实 trace；  
如果没有，先用生成流程 summary。

### 第七步：阶段报告

完成若干关卡后生成报告。

MVP 可先在前端根据进度生成简单报告，后续再接 LLM。

### 第八步：UI 细节统一

最后统一：

```text
卡片阴影
抽屉动画
按钮状态
暗色模式
空状态
加载状态
错误状态
Markdown 样式
公式样式
```

---

## 19. 验证方案

### 19.1 不要默认跑长测试

不要直接跑真实 LLM e2e。  
不要直接触发 HuggingFace 下载。

### 19.2 建议验证

#### 前端

```bash
npm run build
```

如果项目使用 npm prefix：

```bash
npm --prefix agent_edu_platform/frontend-vue run build
```

#### Python 语法检查

```bash
python -m py_compile <changed-python-files>
```

#### 轻量数据验证

检查：

```text
知识图谱 JSON 能否加载
路径推荐函数能否返回节点
schema 能否实例化
```

### 19.3 手动产品验证

用三类用户验证差异。

#### 用户 A：Python 弱、数学弱、偏实践

输入：

```text
Python：几乎没写过
数学：害怕公式
ML：没接触
偏好：先项目实践
方向：系统推荐
```

期望：

```text
从 Python / NumPy / Pandas 或机器学习任务理解开始
讲义少公式
代码解释很细
测验偏基础理解
```

#### 用户 B：Python 中等、ML 弱、偏项目

输入：

```text
Python：会 NumPy/Pandas
数学：基础
ML：没接触
偏好：项目优先
方向：分类预测
```

期望：

```text
跳过 Python 基础
进入数据理解 / sklearn 流程
代码任务较多
理论不过深
```

#### 用户 C：Python 强、数学强、偏理论

输入：

```text
Python：能独立写脚本
数学：能接受推导
ML：跑过 sklearn
偏好：理论优先
方向：深度学习入门
```

期望：

```text
可进入更高级节点
讲义包含公式和原理
测验难度更高
代码解释不必过细
```

---

## 20. 最终期望效果

修改完成后，用户流程应该变成：

```text
用户进入画像页
  ↓
填写 Python / 数学 / ML / 偏好 / 目标方向
  ↓
系统诊断画像
  ↓
进入学习首页 Dashboard
  ↓
看到当前阶段、推荐关卡、分支进度
  ↓
进入当前关卡
  ↓
多 Agent 生成讲义、代码、测验
  ↓
用户学习并向右侧 AI 导师提问
  ↓
完成阅读、代码理解和测验
  ↓
系统更新掌握度
  ↓
生成阶段报告
  ↓
推荐下一关或允许用户切换分支
```

比赛表达时可以总结为：

```text
AgentEdu 构建了一个面向机器学习实训的多 Agent 个性化教育闭环。
系统通过学习者画像识别用户基础，以知识图谱规划共同基础和多分支路径，
通过 RAG 检索约束资源生成，再由生成 Agent 和审核 Agent 协作产出讲义、代码练习和测验。
学习完成后，反馈 Agent 根据测验和用户操作更新掌握度，生成阶段报告并动态调整后续路径。
```

---

## 21. 给修改代码的 AI 的特别提醒

请严格注意：

```text
1. 不要把目标用户写死为“有 Python 基础的人”。
2. 不要把路径设计成单一线性路线。
3. 不要只围绕“逻辑回归”展开。
4. 不要把多 Agent 展示做成满屏技术日志。
5. 不要让 AI 导师主动频繁打扰用户。
6. 不要生成极短模板化讲义。
7. 不要破坏 Markdown 和公式渲染。
8. 不要泄露或提交 .env。
9. 不要默认运行长时间 LLM / e2e 测试。
10. 不要擅自提交 git。
```

优先实现：

```text
画像字段重构
路径推荐逻辑重构
Dashboard 新增
LearningView 模块化
Agent 过程抽屉
阶段报告
```

暂时不要做：

```text
真实注册登录
在线代码运行
教师端
班级管理
复杂知识图谱可视化
多课程支持
商业化功能
```
