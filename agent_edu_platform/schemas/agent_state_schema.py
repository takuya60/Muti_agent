from pydantic import BaseModel, Field


class DiagnosisResult(BaseModel):
    weak_points: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    recommended_level: str = "beginner_plus"
    learning_objectives: list[str] = Field(default_factory=list)
    explanation_strategy: str = "用案例和图解降低理解门槛"


class KnowledgeEvidence(BaseModel):
    source_id: str
    title: str
    content: str
    knowledge_points: list[str] = Field(default_factory=list)
    score: float = Field(default=0.0, ge=0)


class WorkflowState(BaseModel):
    learner_id: str
    learner_profile: dict
    target_algorithm: str
    diagnosis: DiagnosisResult | None = None
    retrieved_knowledge: list[KnowledgeEvidence] = Field(default_factory=list)
    generated_resources: dict | None = None
    reviewer_feedback: str = ""
    review_passed: bool = False
    feedback_decision: dict | None = None
    evaluation: dict | None = None
    agent_events: list[dict] = Field(default_factory=list)
    retry_count: int = 0


class ChatState(BaseModel):
    session_id: str
    user_message: str
    chat_history: list[dict] = Field(default_factory=list)
    current_resource_context: dict | None = None
    next_node: str = ""
    agent_response: str = ""
