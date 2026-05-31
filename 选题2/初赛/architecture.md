# 初赛架构设计：单智能体数学求解系统

> **核心原则**：初赛不强制多 Agent，重点是**跑通全部题目、正确率最大化、批量处理效率和 JSON 稳定性**。架构从简，不过度设计。

---

## 一、初赛评分重点回顾

| 维度 | 权重 | 说明 |
|---|---|---|
| **答案正确性** | **60%** | 答不对就很难高分，这是最核心的 |
| **推理过程** | ~15% | 推理清晰、步骤合理 |
| **创新性** | ~15% | 题型路由、工具校验、自我修正等 |
| **JSON 格式** | 硬性 | 格式错、无法解析直接按未通过处理 |
| **批量处理** | 隐性 | 初赛要处理全部题目，跑不完 = 丢分 |

**初赛核心目标**：用最实际的方式把每道题跑完、答对、格式对。

---

## 二、初赛系统架构


```text
题目文本
  │
  ▼
┌─────────────────────┐
│  1. 题目预处理        │  清洗 LaTeX、提取关键信息
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. 题型识别          │  关键词匹配，选择对应 prompt 模板
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. 调用 Intern-S1   │  带 CoT 要求的 prompt → 获取推理 + 答案
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. 答案提取          │  从模型回复中提取最终答案
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  5. 工具校验 (可选)   │  SymPy 代入验证 / 数值检查
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
  校验通过     校验失败
     │           │
     │           ▼
     │    ┌──────────────┐
     │    │ 6. 修正重试    │  带错误信息重新调用 (最多 2 次)
     │    └──────┬───────┘
     │           │
     ▼           ▼
┌─────────────────────┐
│  7. JSON 格式化输出   │  Pydantic 校验 + 自动修复
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  8. 保存结果 + 日志   │  JSONL 日志 + JSON 结果文件
└─────────────────────┘
```

**注意**：步骤 2（题型识别）和步骤 5（工具校验）是**渐进式加入**的，不是初期必须的。第一版先跑通 3→4→7→8 这条最短路径。

---

## 三、核心模块详解

### 3.1 Intern-S1 API 调用器

这是整个系统的基础，必须**第一个搞定**。

**核心要求**：
- 稳定：失败自动重试，指数退避
- 限流：不要打爆 API
- 超时：单次调用设合理超时（90-120s）
- 日志：每次请求/响应都记录

```python
# core/api_client.py
import time
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class InternS1Client:
    """Intern-S1 API 封装，带重试和日志"""
    
    def __init__(self, api_key: str, base_url: str, model: str = "internlm3-latest"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_retries = 3
        self.retry_delay = 2.0  # 秒
    
    def call(self, problem: str, system_prompt: str = "", temperature: float = 0.3) -> str | None:
        """调用 API，失败自动重试，返回模型回复文本"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": problem})
        
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    timeout=120.0,
                )
                content = response.choices[0].message.content.strip()
                if content:
                    return content
                logger.warning(f"API 返回空内容 (第 {attempt} 次)")
            except Exception as e:
                logger.error(f"API 调用失败 (第 {attempt} 次): {e}")
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"等待 {delay}s 后重试...")
                    time.sleep(delay)
        
        logger.error("API 调用已达最大重试次数，放弃")
        return None
```

### 3.2 Prompt 设计

初赛的 prompt 不需要过于复杂，但必须**要求模型给出清晰的步骤和明确的答案**。

**基础 prompt（通用型）**：
```python
SYSTEM_PROMPT = """你是一个严谨的数学解题助手。请按以下要求回答：
1. 先分析题目的已知条件和求解目标
2. 逐步推理，每一步写清楚依据
3. 在最后明确标出"最终答案：..."
4. 如果需要，使用 LaTeX 公式
5. 不要跳步，不要省略关键步骤"""

def build_solve_prompt(problem_text: str) -> str:
    return f"""请解决以下数学题：

{problem_text}

要求：
1. 逐步推理，写清每一步
2. 最终答案用"最终答案：..."明确标出
3. 如果有多个答案，全部列出"""
```

**针对不同题型的 prompt 增强**（阶段二加入）：

```python
DOMAIN_PROMPTS = {
    "equation": "注意检查方程的所有解，包括可能的复数解。代入原方程验证每个解。",
    "calculus": "积分题注意加上常数 C（不定积分）。求导题注意链式法则。",
    "linear_algebra": "矩阵计算注意维度。特征值问题先写出特征方程。",
    "probability": "注意区分事件是否独立，条件概率用贝叶斯公式。检查概率值是否在 [0,1] 范围。",
    "optimization": "注意约束条件。检查可行域是否为空。检查最优解是否在边界。",
    "proof": "证明题要逻辑严密，每一步给出依据。避免循环论证。",
}
```

### 3.3 答案提取器

模型回复是自由文本，需要从中**稳定地提取最终答案**。

```python
# core/answer_extractor.py
import re

def extract_answer(response: str) -> str:
    """从模型回复中提取最终答案"""
    # 策略 1：匹配"最终答案"标记
    patterns = [
        r"最终答案[：:]\s*(.+?)(?:\n|$)",
        r"答案[是为：:]\s*(.+?)(?:\n|$)",
        r"\\boxed\{(.+?)\}",
        r"因此[，,]?\s*(.+?)(?:\n|$)",
        r"所以[，,]?\s*(.+?)(?:\n|$)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            return matches[-1].strip()  # 取最后一个匹配（通常是最终结论）
    
    # 策略 2：取最后一段非空内容
    lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
    if lines:
        return lines[-1]
    
    return response.strip()
```

### 3.4 JSON 格式化 + Pydantic 校验

**这是硬性要求，格式错就直接 0 分。**

```python
# schemas/solution_schema.py
from pydantic import BaseModel, Field, field_validator

class MathSolution(BaseModel):
    """每道题的输出格式"""
    problem_id: str
    domain: str = "unknown"
    answer: str
    reasoning_summary: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    verification_status: str = "pending"
    
    @field_validator("answer")
    @classmethod
    def answer_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("answer 不能为空")
        return v.strip()
    
    @field_validator("verification_status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        allowed = {"passed", "failed", "partial", "pending", "skipped"}
        if v not in allowed:
            return "pending"
        return v


def format_solution(
    problem_id: str,
    answer: str,
    reasoning: str = "",
    domain: str = "unknown",
    confidence: float = 0.5,
    verification_status: str = "pending",
) -> dict:
    """安全地构造输出 JSON，不会因为格式问题炸掉"""
    try:
        solution = MathSolution(
            problem_id=problem_id,
            domain=domain,
            answer=answer or "无法求解",
            reasoning_summary=reasoning[:500] if reasoning else "",
            confidence=max(0.0, min(1.0, confidence)),
            verification_status=verification_status,
        )
        return solution.model_dump()
    except Exception:
        # 兜底：即使 Pydantic 都报错，也必须输出合法 JSON
        return {
            "problem_id": problem_id,
            "domain": "unknown",
            "answer": str(answer) if answer else "无法求解",
            "reasoning_summary": "",
            "confidence": 0.0,
            "verification_status": "failed",
        }
```

### 3.5 批量处理引擎

初赛要处理全部题目，**跑不完 = 丢分**。必须支持：
- 断点续跑（中断后不需要重头来）
- 每题独立保存（一题崩了不影响其他题）
- 进度显示（知道跑到哪了）

```python
# batch/runner.py
import json
import time
import logging
from pathlib import Path
from tqdm import tqdm

logger = logging.getLogger(__name__)

class BatchRunner:
    def __init__(self, solver, output_dir: str = "data/results"):
        self.solver = solver
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self, problems: list[dict]) -> dict:
        """批量处理所有题目"""
        stats = {"total": len(problems), "done": 0, "skipped": 0, "failed": 0}
        
        for problem in tqdm(problems, desc="批量求解"):
            pid = problem["problem_id"]
            result_file = self.output_dir / f"{pid}.json"
            
            # 断点续跑：已有结果就跳过
            if result_file.exists():
                stats["skipped"] += 1
                stats["done"] += 1
                continue
            
            try:
                result = self.solver.solve(problem)
                result_file.write_text(
                    json.dumps(result, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                stats["done"] += 1
            except Exception as e:
                logger.error(f"题目 {pid} 处理失败: {e}")
                # 失败也保存一个结果，不能丢题
                fallback = {
                    "problem_id": pid,
                    "domain": "unknown",
                    "answer": "无法求解",
                    "reasoning_summary": f"处理异常: {e}",
                    "confidence": 0.0,
                    "verification_status": "failed",
                }
                result_file.write_text(
                    json.dumps(fallback, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                stats["failed"] += 1
                stats["done"] += 1
            
            # 简单限流，避免打爆 API
            time.sleep(0.5)
        
        return stats
```

### 3.6 日志系统

每道题保存完整日志，方便排查和复现。

```python
# logging_system/logger.py
import json
import time
from pathlib import Path
from datetime import datetime

class ProblemLogger:
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    def log(self, entry: dict):
        """追加一条日志"""
        entry["timestamp"] = datetime.now().isoformat()
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

### 3.7 工具校验（渐进式加入）

工具校验**不是初赛第一版必须的**，但加上后能显著提升正确率。建议在基础流程跑通后再加。

优先加 SymPy 代入验证，覆盖面最广：

```python
# tools/sympy_verify.py
import sympy as sp

def verify_equation_solution(equation_str: str, var_name: str, answer_str: str) -> dict:
    """把答案代入方程，检查是否成立"""
    try:
        x = sp.Symbol(var_name)
        eq = sp.sympify(equation_str)
        ans = sp.sympify(answer_str)
        result = sp.simplify(eq.subs(x, ans))
        passed = (result == 0) or (result == True)
        return {"passed": passed, "simplified": str(result)}
    except Exception as e:
        return {"passed": None, "error": str(e)}  # 工具出错不影响流程


def verify_derivative(original: str, var: str, derivative_answer: str) -> dict:
    """验证求导结果：对原函数求导，比较是否一致"""
    try:
        x = sp.Symbol(var)
        f = sp.sympify(original)
        expected = sp.diff(f, x)
        answer = sp.sympify(derivative_answer)
        diff = sp.simplify(expected - answer)
        return {"passed": diff == 0, "expected": str(expected)}
    except Exception as e:
        return {"passed": None, "error": str(e)}
```

---

## 四、初赛主程序入口

```python
# solve.py — 初赛主入口
import json
import logging
from pathlib import Path
from core.api_client import InternS1Client
from core.answer_extractor import extract_answer
from schemas.solution_schema import format_solution
from logging_system.logger import ProblemLogger
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prompt
SYSTEM_PROMPT = """你是一个严谨的数学解题助手。请按以下要求回答：
1. 先分析题目的已知条件和求解目标
2. 逐步推理，每一步写清楚依据
3. 在最后用"最终答案：..."明确标出答案
4. 不要跳步，不要省略关键步骤"""

def solve_one(client: InternS1Client, problem: dict, prob_logger: ProblemLogger) -> dict:
    """解一道题的完整流程"""
    pid = problem["problem_id"]
    text = problem["problem_text"]
    
    # Step 1: 调用 Intern-S1
    prompt = f"请解决以下数学题，逐步推理并在最后明确给出最终答案：\n\n{text}"
    response = client.call(prompt, system_prompt=SYSTEM_PROMPT)
    
    if response is None:
        result = format_solution(pid, "无法求解", "API 调用失败")
        prob_logger.log({"problem_id": pid, "status": "api_failed"})
        return result
    
    # Step 2: 提取答案
    answer = extract_answer(response)
    
    # Step 3: 格式化输出
    result = format_solution(
        problem_id=pid,
        answer=answer,
        reasoning=response,
        confidence=0.6,
        verification_status="pending",
    )
    
    # Step 4: 记日志
    prob_logger.log({
        "problem_id": pid,
        "status": "success",
        "answer": answer,
        "response_length": len(response),
    })
    
    return result


def main():
    # 初始化
    client = InternS1Client(
        api_key=os.getenv("INTERN_S1_API_KEY", ""),
        base_url=os.getenv("INTERN_S1_BASE_URL", ""),
    )
    prob_logger = ProblemLogger()
    
    # 读取题目
    problems_path = Path("data/problems/competition_data")
    # 根据组委会实际数据格式调整读取方式
    problems = []
    for f in sorted(problems_path.glob("*.json")):
        problems.append(json.loads(f.read_text(encoding="utf-8")))
    
    logger.info(f"共 {len(problems)} 道题目")
    
    # 批量处理（带断点续跑）
    output_dir = Path("data/results/solutions")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    done = 0
    skipped = 0
    for problem in problems:
        pid = problem["problem_id"]
        result_file = output_dir / f"{pid}.json"
        
        if result_file.exists():
            skipped += 1
            continue
        
        result = solve_one(client, problem, prob_logger)
        result_file.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        done += 1
        logger.info(f"[{done + skipped}/{len(problems)}] {pid} 完成")
    
    logger.info(f"全部完成：新处理 {done}，跳过 {skipped}，总计 {len(problems)}")


if __name__ == "__main__":
    main()
```

---

## 五、初赛项目目录结构

```text
math_agent_preliminary/
├── core/                         # 核心模块
│   ├── __init__.py
│   ├── api_client.py             # Intern-S1 API 封装 (重试/超时)
│   ├── answer_extractor.py       # 从回复中提取答案
│   └── config.py                 # 配置 (API Key/URL/模型名)
│
├── schemas/
│   ├── __init__.py
│   └── solution_schema.py        # JSON 输出 Pydantic Schema
│
├── tools/                        # 工具校验 (第二步再加)
│   ├── __init__.py
│   └── sympy_verify.py           # SymPy 代入验证
│
├── prompts/
│   └── solve_prompts.py          # Prompt 模板
│
├── logging_system/
│   ├── __init__.py
│   └── logger.py                 # JSONL 日志
│
├── data/
│   ├── problems/                 # 赛题数据
│   ├── results/                  # 输出结果
│   └── logs/                     # 运行日志
│
├── .env                          # API Key
├── .env.example
├── requirements.txt
├── solve.py                      # 主入口 (单题/批量)
└── README.md
```

---

## 六、初赛 requirements.txt

```text
# 必须
openai>=1.30.0
pydantic>=2.7.0
python-dotenv>=1.0.0
tqdm>=4.66.0

# 工具校验 (第二步加入)
sympy>=1.13.0
numpy>=1.26.0

# 可选 (高级校验)
# scipy>=1.14.0
# mpmath>=1.3.0
```

依赖极少，装完就能跑。

---

## 七、开发节奏

```text
Day 1-2：跑通 API
  - 拿到 API Token
  - 写 api_client.py，能调通一道题
  - 写 answer_extractor.py，能从回复中提取答案
  - 写 solution_schema.py，能输出合法 JSON
  - 跑 3-5 道手动测试题，确认流程通

Day 3-4：批量处理
  - 写 solve.py 批量入口
  - 加断点续跑
  - 加 JSONL 日志
  - 用 10-20 道题测试批量流程
  - 统计耗时，评估能否在时间内跑完全部题

Day 5-7：提升正确率
  - 优化 prompt（加题型识别关键词 → 选不同提示）
  - 加 SymPy 代入验证（方程/积分类题优先）
  - 加自我修正（校验失败 → 带错误信息重推 1-2 次）
  - 在更大题目集上测试，统计按领域分组的正确率

Day 8-10：最终调优
  - 分析错误题目，找共性
  - 调 temperature、prompt 措辞
  - 确保所有题目都有输出（即使答不对也不能丢题）
  - 最终提交
```

---

## 八、初赛 vs 决赛的边界

| | 初赛 | 决赛 |
|---|---|---|
| **Agent 数量** | 1 个 (单智能体) | 多个 (Router/Solver/Verifier/Explainer...) |
| **重点** | 正确率 + 效率 + JSON 稳定 | 多 Agent 协作 + 交互 Demo |
| **工具** | SymPy 为主 | SymPy + SciPy + OR-Tools + NetworkX |
| **展示** | 无交互，提交结果文件 | Gradio/Streamlit 交互演示 |
| **代码量** | ~500-800 行 | ~3000+ 行 |
| **框架** | 不需要 LangGraph | 推荐 LangGraph |

**原则**：初赛先做最小可行版本跑出正确率，决赛再拆成多 Agent 展示架构。不要在初赛搞过度设计。
