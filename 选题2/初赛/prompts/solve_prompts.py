SYSTEM_PROMPT = """你是一个严谨的数学解题助手。你必须遵循以下规则：

1. 先分析题目的已知条件、约束和求解目标，不要遗漏任何条件
2. 逐步推理，每一步都写清楚数学依据或定理
3. 计算过程要完整，不要跳步，特别注意正负号和系数
4. 如果题目有多个解，全部列出
5. 在回答的最后，用"最终答案：..."明确标出答案
6. 如果无法求解或信息不足，说明原因并给出你的最佳估计"""

DOMAIN_HINTS = {
    "equation": """
额外注意：
- 检查方程的所有解，包括复数解
- 解完后把每个解代入原方程验证
- 如果是不等式，注意解集的表示
- 分式方程注意检验是否为增根""",
    
    "calculus": """
额外注意：
- 不定积分记得加常数 C
- 定积分检查积分上下限的代入
- 求导注意链式法则、乘法法则
- 极限题先判断是否为未定式，选择合适方法（洛必达/等价无穷小/泰勒展开）
- 级数题先判断收敛性""",

    "linear_algebra": """
额外注意：
- 矩阵运算检查维度是否匹配
- 特征值问题写出特征方程 |A - λI| = 0
- 基础解系要检验线性无关性
- 正交化过程要逐步验证""",
}

GENERAL_ENHANCEMENT = """
最后自查清单：
1. 是否遗漏了题目中的任何条件？
2. 计算过程的正负号是否正确？
3. 答案的量纲/范围是否合理？
4. 最终答案是否用"最终答案：..."标出？"""

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

def build_prompt(problem_text: str, domain: str) -> str:
    """组装最终 prompt"""
    hint = DOMAIN_HINTS.get(domain, "")
    
    prompt = f"请解决以下数学题：\n\n{problem_text}\n"
    if hint:
        prompt += f"\n{hint}\n"
    prompt += f"\n{GENERAL_ENHANCEMENT}"
    
    return prompt

def build_correction_prompt(problem_text: str, previous_answer: str, error_info: str) -> str:
    """组装修正 prompt"""
    return f"""你之前对以下数学题的回答可能有误，请重新检查。

## 题目
{problem_text}

## 你之前的答案（存在问题）
{previous_answer}

## 校验发现的问题
{error_info}

请仔细检查你的推理过程，找出错误并重新给出正确答案。
特别注意计算过程中的正负号、系数和代入步骤。
最后，用"最终答案：..."明确标出修正后的答案。"""
