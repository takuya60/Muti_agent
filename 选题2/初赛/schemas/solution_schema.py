from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger(__name__)

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
            reasoning_summary=reasoning if reasoning else "",
            confidence=max(0.0, min(1.0, confidence)),
            verification_status=verification_status,
        )
        return solution.model_dump()
    except Exception as e:
        logger.error(f"Pydantic 校验失败: {e}")
        # 兜底：即使 Pydantic 都报错，也必须输出合法 JSON
        return {
            "problem_id": problem_id,
            "domain": "unknown",
            "answer": str(answer) if answer else "无法求解",
            "reasoning_summary": "",
            "confidence": 0.0,
            "verification_status": "failed",
        }
