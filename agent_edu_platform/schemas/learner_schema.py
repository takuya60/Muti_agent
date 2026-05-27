from typing import Literal

from pydantic import BaseModel, Field


class LearnerProfile(BaseModel):
    learner_id: str
    name: str
    background: str
    goal: str
    target_algorithm: str = "逻辑回归"
    preferred_style: Literal["案例驱动", "公式推导", "项目挑战", "图解类比"] = "案例驱动"
    available_time_per_week: int = Field(default=4, ge=1, le=40)
    test_scores: dict[str, int] = Field(default_factory=dict)
    known_skills: list[str] = Field(default_factory=list)
    weak_points: list[str] = Field(default_factory=list)
