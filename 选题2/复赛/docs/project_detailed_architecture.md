# XH-202627 基于 Intern-S1 的数学智能体设计与推理创新 - 详尽架构与技术白皮书

本白皮书旨在全面、深度地剖析 MathAgent 系统的技术实现细节，从底层数据结构、算法逻辑到顶层架构设计进行系统性规划。本文档将作为"挑战杯"评委技术审查及后续团队开发的核心参考手册。

---

## 〇、系统宏观架构

系统基于 **多智能体流水线架构 + 数学工具链**，核心运转流如下：

1. **题目输入层**：接收数学题目文本（支持 LaTeX 公式），提取关键信息。
2. **题型路由中枢 (Router Agent)**：基于 Intern-S1 进行题型分类与难度评估，分发至对应求解策略。
3. **求解规划器 (Planner Agent)**：制定解题计划，选择工具组合与验证策略。
4. **多 Solver 协同集群**：Intern-S1 推理 + SymPy/SciPy/OR-Tools 工具链协同求解。
5. **校验-修正闭环 (Verifier Agent)**：符号校验 + 数值验证 + 逻辑审核，失败则反馈错误原因重推。
6. **解释生成器 (Explainer Agent)**：将推理过程转化为启发式教学讲解。
7. **格式化输出器 (Formatter Agent)**：Pydantic 强约束 JSON 输出，自动修复格式错误。
8. **日志与评测系统**：JSONL 全链路日志 + 正确率/耗时/重试统计。

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        MathAgent 系统全景                           │
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │  题目输入  │───▶│ 题型路由  │───▶│ 解题规划  │───▶│  求解器   │      │
│  │  Parser   │    │  Router  │    │ Planner  │    │  Solver  │      │
│  └──────────┘    └──────────┘    └──────────┘    └────┬─────┘      │
│                                                       │             │
│                   ┌───────────────────────────────────┘             │
│                   ▼                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │ 格式输出  │◀───│ 解释生成  │◀───│ 校验修正  │◀───│ 工具调用  │      │
│  │Formatter │    │Explainer │    │ Verifier │    │  Tools   │      │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘      │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────┐    ┌──────────┐                                      │
│  │ JSON输出  │    │ 日志评测  │                                      │
│  │  Result   │    │  Logger  │                                      │
│  └──────────┘    └──────────┘                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 一、核心层级拆解与底层实现

### 1.1 题目解析引擎 (Problem Parser)

将原始题目文本转化为结构化的问题表示。

- **核心文件**：`core/problem_parser.py`
- **数据结构**：`MathProblem` (Pydantic Model)
- **核心能力**：
  - **LaTeX 清洗**：去除冗余格式标记，标准化数学符号表示。
  - **条件提取**：从自然语言中提取已知条件、求解目标、约束条件。
  - **元数据标注**：题目 ID、来源领域、预估难度、关键数学对象（函数、方程、矩阵等）。
- **关键设计**：使用正则表达式 + Intern-S1 辅助提取，双路并行，确保鲁棒性。

```python
class MathProblem(BaseModel):
    problem_id: str
    raw_text: str
    cleaned_text: str
    domain: str | None = None          # 题型领域
    difficulty: str | None = None      # 预估难度
    conditions: list[str] = []         # 已知条件
    objectives: list[str] = []         # 求解目标
    constraints: list[str] = []        # 约束条件
    math_objects: list[str] = []       # 关键数学对象
```

### 1.2 题型路由引擎 (Router Agent)

赛题覆盖 18 个数学子领域，不同题型需要完全不同的求解策略。路由器是系统的"交通枢纽"。

- **核心文件**：`agents/router_agent.py`
- **路由策略**：两级分类

  **第一级 - 粗粒度领域分类：**

  | 领域大类 | 包含子领域 |
  |---|---|
  | 代数与方程 | 线性代数、抽象代数、方程求解 |
  | 分析与微积分 | 微积分、实分析、复分析、泛函分析 |
  | 微分方程 | 常微分方程、偏微分方程 |
  | 离散数学 | 组合数学、图论、数论 |
  | 概率统计 | 概率论、数理统计 |
  | 优化与运筹 | 线性规划、整数规划、非线性优化 |
  | 几何与拓扑 | 微分几何、拓扑学 |

  **第二级 - 细粒度题型判定：**
  基于 Intern-S1 分析题目结构，判定具体的求解类型（计算题、证明题、应用题、判断题等）。

- **核心算法**：
  1. 先用关键词规则快速匹配（高效、确定性强）；
  2. 关键词无法确定时，调用 Intern-S1 进行语义分类（兜底）；
  3. 输出 `RoutingDecision`，包含领域、子领域、题型、推荐 solver 和推荐工具。

```python
class RoutingDecision(BaseModel):
    domain: str                          # 领域大类
    sub_domain: str                      # 子领域
    problem_type: str                    # 计算/证明/应用/判断
    recommended_solver: str              # 推荐求解器
    recommended_tools: list[str] = []    # 推荐工具
    confidence: float = 0.0             # 路由置信度
    reasoning: str = ""                 # 路由理由
```

### 1.3 解题规划器 (Planner Agent)

根据路由结果，制定具体的解题计划。

- **核心文件**：`agents/planner_agent.py`
- **核心能力**：
  - **方法选择**：针对同一题目，可能有多种解法（如用 SymPy 符号解 vs 数值近似解），Planner 选择最优路径。
  - **步骤分解**：将复杂问题分解为可执行的子步骤序列。
  - **工具编排**：决定每个子步骤是调用 LLM 推理还是使用数学工具。
  - **验证策略**：为每个步骤预设验证方法（代入法、数值法、反证法等）。

```python
class SolvingPlan(BaseModel):
    strategy_name: str                   # 策略名称
    steps: list[PlanStep]               # 步骤序列
    verification_method: str            # 主验证方法
    fallback_strategy: str | None       # 备选策略
    estimated_complexity: str           # 预估复杂度
    tools_needed: list[str]             # 所需工具
```

### 1.4 求解器集群 (Solver Agent + Tool Agent)

这是系统的核心生产力，负责实际的数学推理与计算。

- **核心文件**：`agents/solver_agent.py`, `tools/math_tools.py`

#### 1.4.1 Intern-S1 推理求解器

- 调用 Intern-S1 API 进行数学推理。
- 关键策略：**Chain-of-Thought (CoT) 多步推理**，要求模型逐步展示思考过程。
- **Prompt 工程**：针对不同题型设计专用 prompt 模板，包含领域知识提示、格式约束和常见错误警告。

#### 1.4.2 数学工具链

| 工具 | 适用场景 | 核心 API |
|---|---|---|
| **SymPy** | 符号计算：化简、求导、积分、解方程、矩阵运算 | `sympy.solve()`, `sympy.simplify()`, `sympy.integrate()` |
| **NumPy** | 数值计算：矩阵运算、线性代数 | `numpy.linalg`, `numpy.roots()` |
| **SciPy** | 数值积分、微分方程数值解、优化 | `scipy.integrate`, `scipy.optimize` |
| **mpmath** | 高精度数值计算、特殊函数 | `mpmath.mpf()`, `mpmath.quad()` |
| **OR-Tools** | 线性规划、整数规划、约束满足 | `ortools.linear_solver`, `ortools.sat` |
| **PuLP** | 线性规划建模 | `pulp.LpProblem`, `pulp.LpVariable` |
| **NetworkX** | 图论问题：最短路径、网络流、图着色 | `networkx.shortest_path()`, `networkx.max_flow()` |

#### 1.4.3 工具调用协议

```python
class ToolCall(BaseModel):
    tool_name: str                       # 工具名
    function_name: str                   # 调用函数
    arguments: dict                      # 参数
    expected_output_type: str           # 预期输出类型
    timeout_seconds: int = 30           # 超时

class ToolResult(BaseModel):
    tool_name: str
    success: bool
    result: Any | None
    error: str | None = None
    execution_time_ms: int
```

### 1.5 校验-修正闭环 (Verifier Agent)

这是系统正确率的核心保障，也是本项目最大的创新点之一。

- **核心文件**：`agents/verifier_agent.py`
- **三级校验体系**：

  **Level 1 — 符号校验 (SymPy)**：
  - 代入验证：将答案代入原方程/条件，检查等式是否成立。
  - 化简验证：将答案化简，检查与标准形式是否一致。
  - 求导/积分反验证：对积分结果求导，检查是否还原被积函数。

  **Level 2 — 数值校验 (NumPy/mpmath)**：
  - 随机取点代入：在答案的定义域内随机选取多个点，比较左右两端数值。
  - 误差阈值控制：`abs(lhs - rhs) < 1e-8`，支持浮点精度配置。
  - 边界条件检查：在边界值、奇异点附近做特殊验证。

  **Level 3 — 逻辑校验 (Intern-S1)**：
  - 由独立的 Verifier Agent 审核推理链，检查是否有跳步、误用定理、循环论证。
  - 输出结构化的审核报告，标明问题出在哪一步。

- **修正机制**：
  ```text
  Solver 输出答案
    ↓
  Level 1 符号校验
    ↓ (失败)
  Level 2 数值校验
    ↓ (失败)
  Level 3 逻辑校验
    ↓
  提取失败原因 + 错误定位
    ↓
  构造修正 Prompt（含错误信息）
    ↓
  反馈给 Solver 重新推理
    ↓
  最多重试 N 次 (默认 3 次)
    ↓
  选择最高置信度的答案输出
  ```

```python
class VerificationResult(BaseModel):
    level: str                           # symbolic / numerical / logical
    passed: bool
    details: str
    error_location: str | None = None   # 错误定位到第几步
    suggested_fix: str | None = None    # 建议修正方向

class VerificationReport(BaseModel):
    overall_passed: bool
    results: list[VerificationResult]
    confidence: float                    # 综合置信度
    retry_suggested: bool
    error_summary: str | None = None
```

### 1.6 解释生成器 (Explainer Agent)

将机械的推理过程转化为人类可理解的教学讲解，提升主观评分。

- **核心文件**：`agents/explainer_agent.py`
- **讲解结构**：
  1. **题目关键条件**：有哪些已知信息、隐含条件。
  2. **方法选择理由**：为什么选这个方法，而不是其他。
  3. **核心定理/技巧**：用到了哪个定理，为什么适用。
  4. **易错点警示**：哪一步最容易犯错，需要注意什么。
  5. **答案总结**：最终答案是什么，结果的直觉含义。

### 1.7 格式化输出器 (Formatter Agent)

保证 JSON 输出严格合法，这是赛题的硬性要求。

- **核心文件**：`agents/formatter_agent.py`
- **核心策略**：
  - 使用 **Pydantic** 强类型约束，定义严格的输出 Schema。
  - 模型输出后**不直接提交**，先经过格式验证层。
  - 字段缺失、类型错误或 answer 为空时，触发格式修复或重新生成。
  - 最终输出通过 `model.model_validate()` 强制校验。

```python
class MathSolution(BaseModel):
    problem_id: str
    domain: str
    answer: str
    reasoning_summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    verification_status: str             # passed / failed / partial
    steps: list[str] = []               # 推理步骤
    tools_used: list[str] = []          # 使用的工具
    heuristic_explanation: str = ""     # 启发式解释
    retry_count: int = 0               # 重试次数
```

### 1.8 日志与评测系统

- **核心文件**：`logging/logger.py`, `evaluation/evaluator.py`
- **日志策略**：每道题保存完整 JSONL 日志：

```python
class ProblemLog(BaseModel):
    problem_id: str
    timestamp: str
    domain: str                          # 题型
    routing_decision: dict              # 路由决策
    solving_plan: dict                  # 解题计划
    solver_response: str                # 模型回答
    tool_calls: list[dict]              # 工具调用记录
    verification_results: list[dict]    # 校验结果
    final_answer: str                   # 最终答案
    retry_count: int                    # 重试次数
    total_time_ms: int                  # 总耗时
    error: str | None = None           # 错误信息
    status: str                        # success / failed / timeout
```

- **评测指标**：
  - 正确率 (Accuracy)：按领域、难度分层统计。
  - 平均耗时 (Latency)：API 调用时间 + 工具计算时间。
  - 重试率 (Retry Rate)：校验失败后重试的比例。
  - 工具使用率 (Tool Usage)：各工具被调用的频率。
  - 格式合规率 (Format Compliance)：JSON 输出一次通过的比例。

---

## 二、多智能体工作流 (LangGraph StateGraph)

### 2.1 状态总线定义

```python
class MathAgentState(TypedDict, total=False):
    problem: dict                        # 解析后的题目
    routing: dict                        # 路由决策
    plan: dict                           # 解题计划
    solver_output: str                   # 求解器输出
    tool_results: list[dict]            # 工具调用结果
    verification: dict                   # 校验报告
    explanation: str                     # 启发式解释
    final_solution: dict                # 最终解答
    retry_count: int                    # 重试计数
    agent_events: list[dict]            # Agent 事件日志
    error: str | None                   # 错误信息
```

### 2.2 StateGraph 流转图

```text
START
  │
  ▼
[parse] ──────▶ [route] ──────▶ [plan] ──────▶ [solve]
                                                  │
                                                  ▼
                                              [verify]
                                                  │
                                    ┌─────────────┼─────────────┐
                                    ▼             ▼             ▼
                                 passed      retry < N      retry >= N
                                    │             │             │
                                    ▼             ▼             ▼
                              [explain]      [solve]     [best_effort]
                                    │                         │
                                    ▼                         ▼
                              [format] ◀──────────────────────┘
                                    │
                                    ▼
                                  END
```

### 2.3 条件边路由逻辑

```python
def route_after_verify(state: MathAgentState) -> str:
    verification = state.get("verification", {})
    if verification.get("overall_passed"):
        return "explain"
    if state.get("retry_count", 0) >= MAX_RETRY:
        return "best_effort"       # 选择历史最高置信度答案
    return "solve"                 # 重新求解
```

---

## 三、项目目录结构全景解析

```text
math_agent/
├── agents/                           # 🧠 智能体逻辑层
│   ├── __init__.py
│   ├── router_agent.py               # - 18 领域题型路由 Agent
│   ├── planner_agent.py              # - 解题策略规划 Agent
│   ├── solver_agent.py               # - 核心求解 Agent (调用 Intern-S1)
│   ├── tool_agent.py                 # - 数学工具调度 Agent
│   ├── verifier_agent.py             # - 三级校验 Agent
│   ├── explainer_agent.py            # - 启发式解释生成 Agent
│   ├── formatter_agent.py            # - JSON 格式化 Agent
│   ├── graph_state.py                # - LangGraph 状态黑板定义
│   └── workflow.py                   # - 连接所有 Agent 的 StateGraph
│
├── core/                             # ⚙️ 核心基础设施
│   ├── __init__.py
│   ├── problem_parser.py             # - 题目解析与清洗
│   ├── api_client.py                 # - Intern-S1 API 封装 (重试/限流/超时)
│   ├── config.py                     # - 全局配置 (API Key, 模型参数, 阈值)
│   └── retry.py                      # - 通用重试与容错机制
│
├── tools/                            # 🔧 数学工具链
│   ├── __init__.py
│   ├── math_tools.py                 # - 工具调度中心
│   ├── sympy_tools.py                # - SymPy 符号计算封装
│   ├── numpy_tools.py                # - NumPy/SciPy 数值计算封装
│   ├── optimization_tools.py         # - OR-Tools/PuLP 优化工具封装
│   ├── graph_tools.py                # - NetworkX 图论工具封装
│   └── verification_tools.py         # - 校验专用工具 (代入/数值/边界)
│
├── schemas/                          # 📜 数据契约体系
│   ├── __init__.py
│   ├── problem_schema.py             # - 题目结构定义
│   ├── solution_schema.py            # - 解答输出格式定义
│   ├── agent_state_schema.py         # - 工作流流转状态定义
│   └── log_schema.py                 # - 日志记录格式定义
│
├── prompts/                          # 💬 Prompt 模板库
│   ├── router_prompts.py             # - 题型路由 prompt
│   ├── solver_prompts.py             # - 各领域解题 prompt 模板
│   ├── verifier_prompts.py           # - 逻辑校验 prompt
│   ├── explainer_prompts.py          # - 解释生成 prompt
│   └── formatter_prompts.py          # - 格式修复 prompt
│
├── logging_system/                   # 📊 日志与追踪
│   ├── __init__.py
│   ├── logger.py                     # - JSONL 日志记录器
│   └── log_analyzer.py              # - 日志分析与统计
│
├── evaluation/                       # 📈 评测系统
│   ├── __init__.py
│   ├── evaluator.py                  # - 正确率/耗时/重试率评测
│   ├── domain_stats.py              # - 按领域分层统计
│   └── report_generator.py          # - 评测报告生成
│
├── batch/                            # 🔄 批量处理
│   ├── __init__.py
│   ├── batch_runner.py              # - 批量题目处理引擎
│   ├── checkpoint.py                # - 断点续跑机制
│   └── result_aggregator.py         # - 结果汇总
│
├── demo/                             # 🎨 交互展示
│   ├── app.py                        # - Gradio/Streamlit Demo 入口
│   ├── components/                   # - UI 组件
│   │   ├── problem_input.py         #   - 题目输入面板
│   │   ├── process_viewer.py        #   - Agent 过程可视化
│   │   ├── solution_display.py      #   - 解答展示面板
│   │   └── stats_dashboard.py       #   - 统计数据面板
│   └── static/                       # - 静态资源
│
├── data/                             # 📁 数据目录
│   ├── problems/                     # - 题目数据
│   │   ├── sample_problems.json     #   - 样例题目
│   │   └── competition_data/        #   - 赛题数据 (竞赛提供)
│   ├── results/                      # - 运行结果
│   │   └── solutions/               #   - JSON 解答输出
│   └── logs/                         # - 运行日志
│       └── *.jsonl                  #   - JSONL 日志文件
│
├── tests/                            # ✅ 测试
│   ├── test_parser.py               # - 题目解析测试
│   ├── test_router.py               # - 路由测试
│   ├── test_solver.py               # - 求解测试
│   ├── test_verifier.py             # - 校验测试
│   ├── test_formatter.py            # - 格式化测试
│   └── test_e2e.py                  # - 端到端测试
│
├── notebooks/                        # 📓 Jupyter Notebook
│   ├── demo_single_problem.ipynb    # - 单题演示
│   ├── batch_analysis.ipynb         # - 批量结果分析
│   └── domain_breakdown.ipynb       # - 领域分析
│
├── .env                              # - 环境变量 (API Key)
├── .env.example                      # - 环境变量模板
├── requirements.txt                  # - Python 依赖
├── README.md                         # - 项目说明
├── run_single.py                     # - 单题运行入口
├── run_batch.py                      # - 批量运行入口
└── run_demo.py                       # - Demo 启动入口
```

---

## 四、关键技术决策与设计理由

### 4.1 为什么选择 LangGraph 而非纯 lagent

| 维度 | lagent | LangGraph | 决策 |
|---|---|---|---|
| 流程控制 | 依赖框架内部逻辑 | 显式 StateGraph + 条件边 | **LangGraph 更透明** |
| 状态管理 | 隐式 | TypedDict 显式声明 | **LangGraph 更可调试** |
| 条件路由 | 有限 | 任意条件边 | **LangGraph 更灵活** |
| 重试机制 | 需自行实现 | 条件边天然支持循环 | **LangGraph 更优雅** |
| 生态兼容 | LangChain 生态 | LangChain 生态 | 持平 |
| 学习曲线 | 较陡 | 中等 | LangGraph 文档更好 |

**结论**：使用 LangGraph 构建主工作流，但保留对 lagent 的兼容接口（因为官方基线使用 lagent），方便评委理解。

### 4.2 为什么三级校验而非单级

- **符号校验**：精确但覆盖面有限（只适用于有解析解的题）。
- **数值校验**：覆盖面广但有浮点误差。
- **逻辑校验**：能发现推理链问题但依赖 LLM 判断力。
- 三级互补，**单级都无法独立保障正确率**。

### 4.3 API 调用策略

```python
# 核心策略
MAX_RETRIES = 3                      # API 失败重试
RETRY_DELAY_BASE = 2.0               # 指数退避基数
RATE_LIMIT_RPM = 60                  # 每分钟请求上限
TIMEOUT_SECONDS = 120                # 单次调用超时
BATCH_CONCURRENCY = 5                # 批量并发数
```

---

## 五、结论与竞赛价值

MathAgent 系统通过 **"题型路由 + 工具增强推理 + 三级校验闭环"** 这一核心组合，从工程层面最大化了 Intern-S1 的数学推理能力。项目不是简单地堆叠 prompt，而是构建了一套**可验证、可修正、可追踪**的数学智能体系统。

核心竞争力：
1. **题型路由**：18 领域精准分发，而非一个 prompt 打天下。
2. **工具增强**：SymPy/SciPy/OR-Tools 弥补 LLM 计算短板。
3. **闭环校验**：符号 + 数值 + 逻辑三级联合验证。
4. **自我修正**：错误反馈 + 定向重推，而非盲目重试。
5. **稳定输出**：Pydantic 强约束 + 格式修复，JSON 合规率趋近 100%。
6. **全链路可观测**：每题完整日志，支持复现和分析。
