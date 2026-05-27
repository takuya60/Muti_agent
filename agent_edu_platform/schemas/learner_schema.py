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
    mastered_points: list[str] = Field(default_factory=list)
    current_level: str = "beginner_plus"
    
    # 深度增强画像字段
    bloom_taxonomy: dict[str, str] = Field(default_factory=dict)
    learning_style_model: dict[str, str] = Field(default_factory=dict)
    attention_span_minutes: int = Field(default=30)
    frustration_index: float = Field(default=0.0)
    engagement_score: float = Field(default=1.0)
    knowledge_mastery: dict[str, float] = Field(default_factory=dict)
