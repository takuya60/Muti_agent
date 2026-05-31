# XH-202627 数学智能体 - 技术路线与开发计划

---

## 一、技术路线总览

```text
阶段一 (第1-2周)        阶段二 (第2-3周)        阶段三 (第3-5周)
基础搭建                 核心能力                 高级特性
─────────────          ─────────────          ─────────────
├─ API 跑通              ├─ 题型路由              ├─ 三级校验
├─ JSON 输出             ├─ 工具集成              ├─ 自我修正
├─ 日志系统              ├─ 批量处理              ├─ 解释生成
└─ 单题测试              └─ 断点续跑              └─ 多Agent决赛

阶段四 (第5-6周)        阶段五 (第6-7周)
评测优化                 展示准备
─────────────          ─────────────
├─ 正确率分析            ├─ Gradio Demo
├─ 弱领域补强            ├─ 演示脚本
├─ 参数调优              ├─ 文档撰写
└─ 压力测试              └─ 答辩准备
```

---

## 二、各阶段详细计划

### 阶段一：基础搭建（第 1-2 周）

**目标**：跑通 Intern-S1 API，建立基本的单题求解流程。

#### 任务 1.1：环境搭建与 API 对接
```text
- [ ] 申请 Intern-S1 API Token
- [ ] 搭建 Python 项目骨架 (poetry/pip + .env)
- [ ] 封装 API Client (重试、超时、错误处理)
- [ ] 写单元测试验证 API 连通性
```

**关键代码 — API Client 核心设计**：
```python
# core/api_client.py
import time
import logging
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class InternS1Client:
    def __init__(self, api_key: str, base_url: str, model: str = "internlm3-latest"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30))
    def solve(self, problem: str, system_prompt: str = "", temperature: float = 0.3) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": problem})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            timeout=120.0,
        )
        return response.choices[0].message.content.strip()
```

#### 任务 1.2：JSON 输出格式定义
```text
- [ ] 定义 MathSolution Pydantic Schema
- [ ] 实现格式校验函数
- [ ] 实现格式修复函数 (字段缺失自动补全)
- [ ] 写单元测试验证合法/非法 JSON
```

**关键代码 — 输出 Schema**：
```python
# schemas/solution_schema.py
from pydantic import BaseModel, Field

class MathSolution(BaseModel):
    problem_id: str
    domain: str = "unknown"
    answer: str
    reasoning_summary: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    verification_status: str = "pending"  # passed / failed / partial / pending
    steps: list[str] = []
    tools_used: list[str] = []
    heuristic_explanation: str = ""
    retry_count: int = 0
```

#### 任务 1.3：日志系统搭建
```text
- [ ] 定义 ProblemLog Schema
- [ ] 实现 JSONL 日志写入器
- [ ] 实现日志查询器
- [ ] 验证日志可读、可解析
```

#### 任务 1.4：单题端到端测试
```text
- [ ] 手动选 5 道不同领域的题目
- [ ] 用最简流程（直接调 API + 格式化）跑通
- [ ] 确认 JSON 输出合法
- [ ] 确认日志完整
```

**阶段一交付物**：
- 可以稳定调用 Intern-S1 解一道题并输出合法 JSON。
- 完整的日志记录。
- 所有基础 Schema 定义完毕。

---

### 阶段二：核心能力（第 2-3 周）

**目标**：实现题型路由、工具集成、批量处理。

#### 任务 2.1：题型路由器
```text
- [ ] 定义 18 领域分类体系
- [ ] 实现关键词规则路由 (一级)
- [ ] 实现 Intern-S1 语义路由 (二级兜底)
- [ ] 定义每个领域的推荐 solver 和工具
- [ ] 在 20+ 题目上测试路由准确率
```

**关键代码 — 路由核心**：
```python
# agents/router_agent.py
KEYWORD_RULES: dict[str, list[str]] = {
    "linear_algebra": ["矩阵", "行列式", "特征值", "线性空间", "正交"],
    "calculus": ["极限", "导数", "积分", "微分", "泰勒展开"],
    "ode": ["常微分方程", "初值问题", "通解", "特解"],
    "pde": ["偏微分方程", "拉普拉斯", "热方程", "波动方程"],
    "complex_analysis": ["复变函数", "解析", "留数", "柯西", "洛朗级数"],
    "probability": ["概率", "期望", "方差", "分布", "随机变量"],
    "optimization": ["线性规划", "单纯形", "对偶", "整数规划", "目标函数"],
    "graph_theory": ["图", "路径", "连通", "树", "匹配", "着色", "网络流"],
    "number_theory": ["整除", "同余", "素数", "模", "欧拉函数"],
    "combinatorics": ["排列", "组合", "母函数", "容斥", "递推"],
    "topology": ["拓扑", "连续映射", "同胚", "紧致", "连通"],
    "abstract_algebra": ["群", "环", "域", "同态", "商群", "理想"],
    "real_analysis": ["收敛", "一致连续", "列紧", "测度", "勒贝格"],
    "functional_analysis": ["范数", "巴拿赫", "希尔伯特", "算子", "泛函"],
    "differential_geometry": ["曲率", "流形", "切空间", "黎曼"],
    "statistics": ["估计", "假设检验", "置信区间", "回归", "方差分析"],
    "numerical_methods": ["插值", "逼近", "迭代", "收敛阶", "误差"],
    "operations_research": ["运输问题", "指派", "排队", "库存", "动态规划"],
}

def route_by_keywords(problem_text: str) -> str | None:
    scores = {}
    for domain, keywords in KEYWORD_RULES.items():
        score = sum(1 for kw in keywords if kw in problem_text)
        if score > 0:
            scores[domain] = score
    if scores:
        return max(scores, key=scores.get)
    return None
```

#### 任务 2.2：数学工具集成
```text
- [ ] 封装 SymPy 工具 (solve, simplify, diff, integrate, Matrix)
- [ ] 封装 NumPy 工具 (linalg, roots)
- [ ] 封装 SciPy 工具 (odeint, minimize)
- [ ] 封装 OR-Tools 工具 (LP, IP)
- [ ] 封装 NetworkX 工具 (shortest_path, max_flow)
- [ ] 实现统一的 ToolDispatcher
- [ ] 每种工具写 3+ 测试用例
```

**关键代码 — SymPy 工具封装**：
```python
# tools/sympy_tools.py
import sympy as sp
from typing import Any

def verify_equation_solution(equation_str: str, variable: str, solution_str: str) -> dict:
    """代入验证：将解代入方程检查是否成立"""
    try:
        x = sp.Symbol(variable)
        equation = sp.sympify(equation_str)
        solution = sp.sympify(solution_str)
        result = equation.subs(x, solution)
        simplified = sp.simplify(result)
        return {
            "passed": simplified == 0 or simplified == True,
            "substituted": str(simplified),
            "details": f"代入 {variable}={solution_str} 后，方程值为 {simplified}",
        }
    except Exception as e:
        return {"passed": False, "error": str(e)}

def verify_integral(integrand_str: str, variable: str, result_str: str) -> dict:
    """积分反验证：对积分结果求导，检查是否还原"""
    try:
        x = sp.Symbol(variable)
        result = sp.sympify(result_str)
        derivative = sp.diff(result, x)
        integrand = sp.sympify(integrand_str)
        diff = sp.simplify(derivative - integrand)
        return {
            "passed": diff == 0,
            "derivative": str(derivative),
            "difference": str(diff),
        }
    except Exception as e:
        return {"passed": False, "error": str(e)}
```

#### 任务 2.3：批量处理引擎
```text
- [ ] 实现 BatchRunner (读取题目 → 循环调用 → 保存结果)
- [ ] 实现断点续跑 (checkpoint 机制)
- [ ] 实现并发控制 (asyncio + semaphore)
- [ ] 实现进度显示 (tqdm)
- [ ] 实现结果汇总 (正确率、耗时统计)
```

**关键代码 — 断点续跑**：
```python
# batch/checkpoint.py
import json
from pathlib import Path

class Checkpoint:
    def __init__(self, checkpoint_path: str = "data/checkpoint.json"):
        self.path = Path(checkpoint_path)
        self.completed: set[str] = set()
        self._load()

    def _load(self):
        if self.path.exists():
            data = json.loads(self.path.read_text())
            self.completed = set(data.get("completed", []))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({
            "completed": list(self.completed)
        }, ensure_ascii=False, indent=2))

    def is_done(self, problem_id: str) -> bool:
        return problem_id in self.completed

    def mark_done(self, problem_id: str):
        self.completed.add(problem_id)
        self.save()
```

**阶段二交付物**：
- 题型路由可以区分 18 个领域。
- SymPy/NumPy/SciPy/OR-Tools/NetworkX 工具封装完毕。
- 批量处理引擎支持断点续跑。

---

### 阶段三：高级特性（第 3-5 周）

**目标**：实现三级校验、自我修正、解释生成、多 Agent 工作流。

#### 任务 3.1：三级校验系统
```text
- [ ] 实现 Level 1 符号校验 (SymPy 代入/化简/反验证)
- [ ] 实现 Level 2 数值校验 (随机取点/边界检查/误差阈值)
- [ ] 实现 Level 3 逻辑校验 (Intern-S1 推理链审核)
- [ ] 实现校验结果聚合与置信度计算
- [ ] 在 50+ 题目上测试校验准确性
```

#### 任务 3.2：自我修正闭环
```text
- [ ] 实现错误定位 (确定推理链中哪一步出错)
- [ ] 实现修正 Prompt 构造 (包含错误信息和修正方向)
- [ ] 实现多轮重试与最优解选择
- [ ] 实现重试日志追踪
- [ ] 在 20+ 失败案例上测试修正效果
```

**关键代码 — 修正 Prompt 构造**：
```python
# agents/solver_agent.py
def build_correction_prompt(
    problem: str,
    previous_answer: str,
    verification_report: dict,
) -> str:
    error_details = verification_report.get("error_summary", "未知错误")
    error_location = verification_report.get("results", [{}])[0].get("error_location", "")

    return f"""
你之前对这道数学题的回答存在问题，请仔细检查并重新推理。

## 原始题目
{problem}

## 你的上一次回答
{previous_answer}

## 校验发现的问题
{error_details}

{f"## 错误可能出在第 {error_location} 步" if error_location else ""}

## 修正要求
1. 仔细检查你上一次的推理过程。
2. 找出错误的步骤并修正。
3. 重新给出完整的推理和最终答案。
4. 特别注意计算过程中的正负号、系数、边界条件。
"""
```

#### 任务 3.3：解释生成 Agent
```text
- [ ] 设计解释 prompt 模板 (五段式结构)
- [ ] 实现解释生成
- [ ] 在 10+ 题目上验证解释质量
```

#### 任务 3.4：完整 LangGraph 工作流
```text
- [ ] 定义 MathAgentState TypedDict
- [ ] 实现 7 个节点函数
- [ ] 实现条件边路由逻辑
- [ ] 构建 StateGraph 并 compile
- [ ] 端到端测试 10+ 题目
```

**阶段三交付物**：
- 三级校验系统可以识别常见错误。
- 自我修正可以提升 10-20% 正确率。
- 完整的 LangGraph 多 Agent 工作流。

---

### 阶段四：评测优化（第 5-6 周）

**目标**：用大量题目评测系统，针对弱项优化。

#### 任务 4.1：大规模评测
```text
- [ ] 在组委会提供的全部题目上运行
- [ ] 按 18 领域分层统计正确率
- [ ] 分析失败原因分布 (推理错误/计算错误/格式错误/超时)
- [ ] 生成评测报告
```

#### 任务 4.2：弱领域针对性优化
```text
- [ ] 识别正确率最低的 3-5 个领域
- [ ] 为这些领域设计专用 prompt
- [ ] 增加该领域的工具覆盖
- [ ] 重新评测验证改善效果
```

#### 任务 4.3：参数调优
```text
- [ ] temperature 对不同题型的最优值
- [ ] 重试次数与正确率/耗时的权衡
- [ ] 校验阈值调优
- [ ] 并发数与稳定性的权衡
```

**阶段四交付物**：
- 全领域正确率报告。
- 针对弱领域的定向优化。
- 最优参数配置。

---

### 阶段五：展示准备（第 6-7 周）

**目标**：准备决赛 Demo 和答辩材料。

#### 任务 5.1：Gradio/Streamlit Demo
```text
- [ ] 题目输入面板 (支持 LaTeX 预览)
- [ ] 题型识别结果展示
- [ ] 解题计划展示
- [ ] Agent 过程可视化 (调用了哪些 solver/verifier)
- [ ] 校验过程展示
- [ ] 最终答案展示
- [ ] 启发式解释展示
- [ ] JSON 输出展示
- [ ] 统计数据面板 (正确率/耗时/领域分布)
```

#### 任务 5.2：演示脚本
```text
- [ ] 准备 3 道不同难度/领域的演示题
- [ ] 准备演示话术
- [ ] 准备异常处理预案
```

#### 任务 5.3：文档与答辩
```text
- [ ] 技术文档终版
- [ ] 答辩 PPT
- [ ] 代码清理与注释
```

---

## 三、技术栈完整清单

| 分类 | 技术 | 版本建议 | 用途 |
|---|---|---|---|
| **语言** | Python | 3.10+ | 主开发语言 |
| **核心模型** | Intern-S1 API | - | 数学推理 |
| **Agent 框架** | LangGraph | 0.2+ | 多 Agent 工作流编排 |
| **辅助框架** | lagent | latest | 兼容官方基线 |
| **符号计算** | SymPy | 1.13+ | 符号化简/求解/验证 |
| **数值计算** | NumPy | 1.26+ | 矩阵/数值运算 |
| **科学计算** | SciPy | 1.14+ | ODE/优化/积分 |
| **高精度** | mpmath | 1.3+ | 高精度数值 |
| **优化** | OR-Tools | 9.10+ | 线性/整数规划 |
| **优化** | PuLP | 2.9+ | LP 建模 |
| **图论** | NetworkX | 3.3+ | 图论问题 |
| **Schema** | Pydantic | 2.7+ | 数据验证 |
| **HTTP** | httpx / openai | - | API 调用 |
| **重试** | tenacity | 9.0+ | 自动重试 |
| **日志** | logging + JSONL | stdlib | 结构化日志 |
| **Demo** | Gradio / Streamlit | latest | 交互展示 |
| **测试** | pytest | 8.0+ | 单元/集成测试 |
| **进度** | tqdm | 4.66+ | 进度条 |
| **异步** | asyncio | stdlib | 批量并发 |

---

## 四、requirements.txt 参考

```text
# Core
openai>=1.30.0
langchain>=0.2.0
langgraph>=0.2.0
pydantic>=2.7.0
python-dotenv>=1.0.0

# Math Tools
sympy>=1.13.0
numpy>=1.26.0
scipy>=1.14.0
mpmath>=1.3.0
ortools>=9.10.0
pulp>=2.9.0
networkx>=3.3.0

# Agent Framework (兼容官方基线)
lagent>=0.5.0

# Utilities
tenacity>=9.0.0
tqdm>=4.66.0
httpx>=0.27.0

# Demo
gradio>=5.0.0
# streamlit>=1.38.0  # 二选一

# Testing
pytest>=8.0.0
pytest-asyncio>=0.24.0
```

---

## 五、风险与应对

| 风险 | 影响 | 应对措施 |
|---|---|---|
| API 调用不稳定 | 批量处理中断 | 指数退避重试 + 断点续跑 |
| 数学题正确率不够 | 得分低 | 三级校验 + 自我修正 + 工具增强 |
| JSON 格式不合规 | 被判未通过 | Pydantic 强约束 + 自动修复 |
| 高级数学题超出工具能力 | 无法用工具校验 | 退化为 LLM 逻辑校验 |
| API 限流 | 批量处理变慢 | 并发控制 + 速率限制 |
| 复杂证明题 | LLM 推理不可靠 | 增加逻辑校验权重 + 多次采样 |
