import re

def extract_answer(response: str) -> str:
    """从模型回复中提取最终答案"""
    if not response:
        return "无法提取答案"
        
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
