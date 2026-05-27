from sqlalchemy.orm import Session
from backend.models import Learner
from schemas.learner_schema import LearnerProfile

def get_learner(db: Session, learner_id: str):
    return db.query(Learner).filter(Learner.id == learner_id).first()

def get_all_learners(db: Session):
    return db.query(Learner).all()

def create_or_update_learner(db: Session, profile: LearnerProfile):
    learner = get_learner(db, profile.learner_id)
    if not learner:
        learner = Learner(id=profile.learner_id)
        db.add(learner)
        
    learner.name = profile.name
    learner.background = profile.background
    learner.goal = profile.goal
    learner.preferred_style = profile.preferred_style
    learner.test_scores = profile.test_scores
    learner.known_skills = profile.known_skills
    learner.weak_points = profile.weak_points
    # mastered_points will be managed incrementally by session/quiz
    
    db.commit()
    db.refresh(learner)
    return learner
