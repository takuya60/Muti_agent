# 初赛 Prompt 工程指南

> 初赛的核心不是 Agent 架构，是 **prompt 写得好不好**。一个好的 prompt 直接决定正确率。

---

## 一、通用 System Prompt

这个 prompt 对所有题型生效：

```python
SYSTEM_PROMPT = """你是一个严谨的数学解题助手。你必须遵循以下规则：

1. 先分析题目的已知条件、约束和求解目标，不要遗漏任何条件
2. 逐步推理，每一步都写清楚数学依据或定理
3. 计算过程要完整，不要跳步，特别注意正负号和系数
4. 如果题目有多个解，全部列出
5. 在回答的最后，用"最终答案：..."明确标出答案
6. 如果无法求解或信息不足，说明原因并给出你的最佳估计"""
```

**为什么这么写**：
- "不要遗漏任何条件"：防止模型忽略隐含条件
- "写清楚数学依据"：让推理过程可追踪，也方便后续检查
- "不要跳步"：跳步是 LLM 出错的主要原因
- "正负号和系数"：LLM 最常犯的计算错误
- "最终答案：..."：给答案提取器一个稳定的锚点

---

## 二、题型识别与路由

先用**关键词规则**判断题型，不需要调用 LLM：

```python
def identify_domain(problem_text: str) -> str:
    """关键词匹配题型，不用 LLM"""
    rules = [
        ("equation",        ["方程", "解", "根", "x =", "求解"]),
        ("calculus",         ["极限", "导数", "积分", "微分", "泰勒", "级数"]),
        ("linear_algebra",   ["矩阵", "行列式", "特征值", "线性空间", "秩"]),
        ("probability",      ["概率", "期望", "方差", "分布", "随机变量"]),
        ("ode",              ["微分方程", "通解", "特解", "初值"]),
        ("pde",              ["偏微分", "拉普拉斯", "热方程", "波动"]),
        ("optimization",     ["规划", "最优", "极值", "约束", "目标函数"]),
        ("graph_theory",     ["图", "路径", "连通", "网络流", "匹配"]),
        ("complex_analysis", ["复变", "解析", "留数", "柯西", "洛朗"]),
        ("number_theory",    ["整除", "同余", "素数", "模"]),
        ("combinatorics",    ["排列", "组合", "容斥", "递推", "母函数"]),
        ("proof",            ["证明", "证：", "试证", "推导"]),
    ]
    
    scores = {}
    for domain, keywords in rules:
        score = sum(1 for kw in keywords if kw in problem_text)
        if score > 0:
            scores[domain] = score
    
    return max(scores, key=scores.get) if scores else "general"
```

---

## 三、按题型增强 Prompt

识别出题型后，在通用 prompt 基础上**追加领域专用提示**：

### 3.1 方程 / 代数

```python
EQUATION_HINT = """
额外注意：
- 检查方程的所有解，包括复数解
- 解完后把每个解代入原方程验证
- 如果是不等式，注意解集的表示
- 分式方程注意检验是否为增根"""
```

### 3.2 微积分

```python
CALCULUS_HINT = """
额外注意：
- 不定积分记得加常数 C
- 定积分检查积分上下限的代入
- 求导注意链式法则、乘法法则
- 极限题先判断是否为未定式，选择合适方法（洛必达/等价无穷小/泰勒展开）
- 级数题先判断收敛性"""
```

### 3.3 线性代数

```python
LINEAR_ALGEBRA_HINT = """
额外注意：
- 矩阵运算检查维度是否匹配
- 特征值问题写出特征方程 |A - λI| = 0
- 基础解系要检验线性无关性
- 正交化过程要逐步验证"""
```

### 3.4 概率统计

```python
PROBABILITY_HINT = """
额外注意：
- 检查概率值是否在 [0,1] 范围
- 区分独立事件和条件概率
- 全概率公式和贝叶斯公式不要搞混
- 期望计算要列清所有可能取值"""
```

### 3.5 微分方程

```python
ODE_HINT = """
额外注意：
- 先判断方程类型（一阶线性/齐次/伯努利/可分离变量/高阶）
- 通解不要忘记任意常数
- 有初值条件时代入求常数
- 结果代入原方程验证"""
```

### 3.6 优化 / 运筹学

```python
OPTIMIZATION_HINT = """
额外注意：
- 先明确目标函数和约束条件
- 检查可行域是否为空
- 线性规划检查角点
- 无约束优化检查驻点和边界"""
```

### 3.7 证明题

```python
PROOF_HINT = """
额外注意：
- 每一步给出明确的定理或引理依据
- 避免循环论证
- 如果用反证法，先明确假设
- 数学归纳法要完整（基始 + 归纳假设 + 归纳步骤）
- 最终答案写"证毕"或"Q.E.D."""
```

### 3.8 通用增强（所有题型都加）

```python
GENERAL_ENHANCEMENT = """
最后自查清单：
1. 是否遗漏了题目中的任何条件？
2. 计算过程的正负号是否正确？
3. 答案的量纲/范围是否合理？
4. 最终答案是否用"最终答案：..."标出？"""
```

---

## 四、Prompt 组装

```python
DOMAIN_HINTS = {
    "equation": EQUATION_HINT,
    "calculus": CALCULUS_HINT,
    "linear_algebra": LINEAR_ALGEBRA_HINT,
    "probability": PROBABILITY_HINT,
    "ode": ODE_HINT,
    "pde": ODE_HINT,  # PDE 和 ODE 提示相近
    "optimization": OPTIMIZATION_HINT,
    "proof": PROOF_HINT,
}

def build_prompt(problem_text: str, domain: str) -> str:
    """组装最终 prompt"""
    hint = DOMAIN_HINTS.get(domain, "")
    
    prompt = f"请解决以下数学题：\n\n{problem_text}\n"
    if hint:
        prompt += f"\n{hint}\n"
    prompt += f"\n{GENERAL_ENHANCEMENT}"
    
    return prompt
```

---

## 五、修正 Prompt（校验失败时用）

如果 SymPy 校验发现答案有误，构造修正 prompt 让模型重试：

```python
def build_correction_prompt(problem_text: str, previous_answer: str, error_info: str) -> str:
    return f"""你之前对以下数学题的回答可能有误，请重新检查。

## 题目
{problem_text}

## 你之前的答案
{previous_answer}

## 校验发现的问题
{error_info}

请仔细检查你的推理过程，找出错误并重新给出正确答案。
特别注意计算过程中的正负号、系数和代入步骤。
用"最终答案：..."标出修正后的答案。"""
```

---

## 六、Prompt 调优经验

| 做法 | 效果 | 原因 |
|---|---|---|
| ✅ 要求"逐步推理" | 提升正确率 | CoT 让模型减少跳步 |
| ✅ 要求"写清依据" | 提升可追踪性 | 方便发现推理错误 |
| ✅ 要求"最终答案：..." | 提升提取成功率 | 给正则一个稳定锚点 |
| ✅ 加领域专用提示 | 减少特定类型错误 | 提醒模型注意常见坑 |
| ✅ 加自查清单 | 轻微提升 | 让模型做最后检查 |
| ❌ prompt 太长 | 可能降低 | 模型注意力被分散 |
| ❌ 要求多种格式 | 降低稳定性 | 增加模型输出负担 |
| ❌ 堆叠无关指令 | 无用或负面 | 噪音太多 |

### temperature 建议

| 题型 | temperature | 理由 |
|---|---|---|
| 计算题 | 0.1 - 0.3 | 需要确定性，不需要创造性 |
| 证明题 | 0.3 - 0.5 | 需要一定灵活性选择方法 |
| 应用题 | 0.2 - 0.4 | 需要理解题意，适度灵活 |
| **默认** | **0.3** | 兼顾准确性和灵活性 |
