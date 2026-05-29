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
    learner.background = _build_background_summary(profile)
    learner.goal = profile.goal
    learner.preferred_style = profile.preferred_style
    learner.test_scores = profile.test_scores
    learner.known_skills = profile.known_skills
    learner.weak_points = profile.weak_points
    learner.mastered_points = profile.mastered_points
    learner.current_level = profile.current_level
    learner.bloom_taxonomy = profile.bloom_taxonomy
    learner.learning_style_model = {
        **profile.learning_style_model,
        "python_level": profile.python_level,
        "math_level": profile.math_level,
        "ml_level": profile.ml_level,
        "practice_preference": profile.practice_preference,
        "theory_preference": profile.theory_preference,
        "target_direction": profile.target_direction,
        "current_confusion": profile.current_confusion,
    }
    learner.attention_span_minutes = profile.attention_span_minutes
    learner.frustration_index = profile.frustration_index
    learner.engagement_score = profile.engagement_score
    learner.knowledge_mastery = profile.knowledge_mastery

    db.commit()
    db.refresh(learner)
    return learner


def _build_background_summary(profile: LearnerProfile) -> str:
    parts = [profile.background] if profile.background else []
    parts.extend([
        f"Python基础={profile.python_level}",
        f"数学基础={profile.math_level}",
        f"机器学习基础={profile.ml_level}",
        f"实践偏好={profile.practice_preference}",
        f"理论偏好={profile.theory_preference}",
        f"目标方向={profile.target_direction}",
    ])
    if profile.current_confusion:
        parts.append(f"当前困惑={profile.current_confusion}")
    return "；".join(parts)
