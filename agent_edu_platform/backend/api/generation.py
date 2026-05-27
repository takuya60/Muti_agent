from fastapi import APIRouter

from agents.workflow import run_workflow
from schemas.learner_schema import LearnerProfile


router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/run")
def generate_resources(profile: LearnerProfile) -> dict:
    state = run_workflow(profile)
    return state.model_dump()
