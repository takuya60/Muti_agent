import argparse
import json
import logging
from pathlib import Path
from tqdm import tqdm

from core.api_client import LLMClient
from core.answer_extractor import extract_answer
from core.config import settings
from schemas.solution_schema import format_solution
from prompts.solve_prompts import SYSTEM_PROMPT, identify_domain, build_prompt, build_correction_prompt
from logging_system.logger import ProblemLogger
from tools.sympy_verify import perform_verification

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def solve_one(client: LLMClient, problem: dict, prob_logger: ProblemLogger) -> dict:
    """解一道题的完整流程"""
    pid = problem.get("problem_id", "unknown_id")
    text = problem.get("problem_text", "")
    
    if not text:
        logger.warning(f"题目 {pid} 缺少文本内容")
        return format_solution(pid, "无法求解", "缺少题目文本")
        
    domain = identify_domain(text)
    prompt = build_prompt(text, domain)
    
    # 调用模型
    response = client.call(prompt, system_prompt=SYSTEM_PROMPT)
    
    if not response:
        result = format_solution(pid, "无法求解", "API 调用失败", domain=domain)
        prob_logger.log({"problem_id": pid, "status": "api_failed", "domain": domain})
        return result
    
    # 提取答案
    answer = extract_answer(response)
    
    # 验证与修正
    verification_status = "pending"
    v_result = perform_verification(domain, text, answer)
    
    if v_result.get("passed") is False:
        logger.info(f"题目 {pid} 第一次验证失败，尝试修正...")
        error_info = v_result.get("simplified") or v_result.get("error") or "结果不一致"
        correction_prompt = build_correction_prompt(text, answer, f"化简或验证结果显示：{error_info}")
        
        correction_response = client.call(correction_prompt, system_prompt=SYSTEM_PROMPT)
        if correction_response:
            response = correction_response
            answer = extract_answer(response)
            # 二次验证
            v_result2 = perform_verification(domain, text, answer)
            if v_result2.get("passed") is True:
                verification_status = "passed_after_retry"
            else:
                verification_status = "failed_after_retry"
        else:
            verification_status = "failed_retry_api_error"
    elif v_result.get("passed") is True:
        verification_status = "passed"
    else:
        verification_status = "skipped_or_unsupported"
    
    # 格式化输出
    result = format_solution(
        problem_id=pid,
        answer=answer,
        reasoning=response,
        domain=domain,
        confidence=0.6,
        verification_status=verification_status,
    )
    
    # 记日志
    prob_logger.log({
        "problem_id": pid,
        "status": "success",
        "domain": domain,
        "answer": answer,
        "response_length": len(response),
    })
    
    return result

def main():
    parser = argparse.ArgumentParser(description="MathAgent 初赛主程序")
    parser.add_argument("--problem", type=str, help="直接输入一道数学题文本")
    parser.add_argument("--batch", type=str, help="批量处理题目目录路径")
    parser.add_argument("--output", type=str, default=settings.RESULTS_DIR, help="结果输出目录")
    
    args = parser.parse_args()
    
    client = LLMClient()
    prob_logger = ProblemLogger(settings.LOGS_DIR)
    
    if args.problem:
        # 单题模式
        problem = {"problem_id": "test_001", "problem_text": args.problem}
        logger.info(f"开始求解: {args.problem}")
        result = solve_one(client, problem, prob_logger)
        print("\n最终结果 JSON:\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.batch:
        # 批量模式
        problems_path = Path(args.batch)
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        problems = []
        for f in sorted(problems_path.glob("*.*")):
            if f.suffix not in ['.tex', '.txt', '.md']:
                continue
            try:
                text = f.read_text(encoding="utf-8")
                problems.append({"problem_id": f.stem, "problem_text": text})
            except Exception as e:
                logger.error(f"无法读取文件 {f}: {e}")
                
        logger.info(f"共发现 {len(problems)} 道题目")
        
        done, skipped, failed = 0, 0, 0
        
        for problem in tqdm(problems, desc="批量求解"):
            pid = problem.get("problem_id")
            if not pid:
                continue
                
            result_file = output_dir / f"{pid}.md"
            if result_file.exists():
                skipped += 1
                continue
                
            try:
                result = solve_one(client, problem, prob_logger)
                
                md_content = f"# {pid} 解答\n\n"
                md_content += f"## 最终答案\n\n{result.get('answer', '')}\n\n"
                md_content += f"## 验证状态\n\n{result.get('verification_status', '')}\n\n"
                md_content += f"## 推理过程\n\n{result.get('reasoning_summary', '')}\n"
                
                result_file.write_text(md_content, encoding="utf-8")
                done += 1
            except Exception as e:
                logger.error(f"题目 {pid} 处理异常: {e}")
                
                md_content = f"# {pid} 处理失败\n\n"
                md_content += f"异常信息: {e}\n"
                result_file.write_text(md_content, encoding="utf-8")
                
                failed += 1
        
        logger.info(f"批量处理完成：成功 {done}，跳过 {skipped}，失败 {failed}，总计 {len(problems)}")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
