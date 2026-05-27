from fastapi import APIRouter

from evaluation.metrics import evaluate_resources
from schemas.agent_state_schema import WorkflowState


router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/score")
def score_state(state: WorkflowState) -> dict:
    return evaluate_resources(state).model_dump()
