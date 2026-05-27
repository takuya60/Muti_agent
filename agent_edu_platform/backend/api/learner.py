from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from schemas.learner_schema import LearnerProfile
from backend.services import learner_service

router = APIRouter(prefix="/learners", tags=["learners"])

@router.get("/examples")
def list_example_profiles(db: Session = Depends(get_db)):
    """从数据库获取所有已注册的画像示例"""
    learners = learner_service.get_all_learners(db)
    return [
        {
            "profile_name": l.name,
            "learner_id": l.id,
            "name": l.name,
            "goal": l.goal,
        }
        for l in learners
    ]

@router.get("/{learner_id}")
def get_learner_profile(learner_id: str, db: Session = Depends(get_db)):
    learner = learner_service.get_learner(db, learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    return learner

@router.post("/validate")
def validate_profile(profile: LearnerProfile, db: Session = Depends(get_db)) -> dict:
    # 模拟验证并保存到数据库
    learner = learner_service.create_or_update_learner(db, profile)
    return {"valid": True, "profile": profile.model_dump(), "saved": True}
