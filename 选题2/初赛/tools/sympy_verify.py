import sympy as sp

def verify_equation_solution(equation_str: str, var_name: str, answer_str: str) -> dict:
    """
    把答案代入方程，检查是否成立。
    适用于形如 'x^2 - 5x + 6 = 0' 或简单的表达式。
    
    返回字典:
    {
        "passed": bool | None, # True: 验证通过, False: 验证失败, None: 工具无法解析
        "simplified": str,     # 化简后的结果字符串
        "error": str           # 如果报错，返回错误信息
    }
    """
    try:
        # 处理等号
        if "=" in equation_str:
            lhs, rhs = equation_str.split("=", 1)
            eq_expr = f"({lhs}) - ({rhs})"
        else:
            eq_expr = equation_str
            
        x = sp.Symbol(var_name)
        eq = sp.sympify(eq_expr)
        ans = sp.sympify(answer_str)
        
        # 代入并化简
        result = sp.simplify(eq.subs(x, ans))
        passed = (result == 0) or (result == True)
        
        return {"passed": passed, "simplified": str(result), "error": None}
    except Exception as e:
        return {"passed": None, "simplified": "", "error": str(e)}

def verify_derivative(original: str, var_name: str, derivative_answer: str) -> dict:
    """
    验证求导结果：对原函数求导，比较是否与给定的导数一致。
    """
    try:
        x = sp.Symbol(var_name)
        f = sp.sympify(original)
        expected = sp.diff(f, x)
        answer = sp.sympify(derivative_answer)
        
        # 比较差值是否为0
        diff = sp.simplify(expected - answer)
        passed = (diff == 0)
        
        return {"passed": passed, "expected": str(expected), "error": None}
    except Exception as e:
        return {"passed": None, "expected": "", "error": str(e)}

def perform_verification(domain: str, problem_text: str, answer: str) -> dict:
    """
    简单的路由：根据领域和题目内容决定是否尝试验证。
    由于初赛不强依赖复杂工具链，这里只做最简单的规则判断。
    """
    if domain == "equation" and "x" in answer:
        # 极其简化的启发式：尝试提取 x= 后的部分
        ans_part = answer.split("x=")[-1].strip() if "x=" in answer else answer
        return verify_equation_solution(problem_text, "x", ans_part)
        
    return {"passed": None, "error": "暂无适用的验证工具"}
