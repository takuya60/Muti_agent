from fastapi import APIRouter
from pydantic import BaseModel

from agents.workflow import run_workflow
from schemas.learner_schema import LearnerProfile


class FeedbackRequest(BaseModel):
    profile: LearnerProfile
    quiz_accuracy: float | None = None
    learner_feedback: str = ""


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/decide")
def decide_next_step(request: FeedbackRequest) -> dict:
    state = run_workflow(
        request.profile,
        quiz_accuracy=request.quiz_accuracy,
        learner_feedback=request.learner_feedback,
    )
    return state.feedback_decision or {}
