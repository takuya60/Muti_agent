from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    hallucination_risk: str = "low"
    hallucination_rate: float = Field(default=0.0, ge=0, le=1)
    difficulty_match: float = Field(default=0.0, ge=0, le=1)
    knowledge_coverage: float = Field(default=0.0, ge=0, le=1)
    structure_completeness: float = Field(default=0.0, ge=0, le=1)
    notes: list[str] = Field(default_factory=list)
