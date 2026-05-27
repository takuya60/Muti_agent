from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession
from backend.database import get_db
from backend.services import session_service
from schemas.session_schema import SessionCreate

from agents.workflow import run_workflow
from schemas.learner_schema import LearnerProfile

router = APIRouter(prefix="/generation", tags=["generation"])

@router.post("/run")
def generate_resources(profile: LearnerProfile, db: DbSession = Depends(get_db)) -> dict:
    session_in = SessionCreate(
        learner_id=profile.learner_id,
        target_algorithm="logistic_regression"
    )
    db_session = session_service.create_session(db, session_in)
    
    state = run_workflow(profile)
    
    db_session.generated_resources = state.generated_resources
    if state.diagnosis:
        db_session.diagnosis_summary = state.diagnosis.model_dump()
    db.commit()
    
    res = state.model_dump()
    res["session_id"] = db_session.id
    return res
