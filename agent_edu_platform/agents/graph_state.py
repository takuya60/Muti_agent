from __future__ import annotations

from typing import TypedDict

from schemas.agent_state_schema import DiagnosisResult, KnowledgeEvidence

# langGraph的全局State
class AgentGraphState(TypedDict, total=False):
    learner_id: str
    learner_profile: dict
    target_algorithm: str
    diagnosis: DiagnosisResult
    retrieved_knowledge: list[KnowledgeEvidence]
    generated_resources: dict
    reviewer_feedback: str
    review_passed: bool
    feedback_decision: dict
    evaluation: dict
    retry_count: int
    quiz_accuracy: float | None
    learner_feedback: str
    agent_events: list[dict]
