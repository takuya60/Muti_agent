from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession
from backend.database import get_db
from backend.services import session_service
from backend.models import Session
from schemas.session_schema import SessionCreate

from agents.workflow import run_workflow
from agents.path_planner import build_learning_plan, recommend_current_node, build_path_for_direction, resolve_direction, infer_mastered_nodes
from knowledge_graph.graph_builder import KnowledgeGraphManager
from schemas.learner_schema import LearnerProfile

router = APIRouter(prefix="/generation", tags=["generation"])

_kg = KnowledgeGraphManager()


def _compute_current_node(profile: LearnerProfile) -> str:
    """根据学习者画像计算当前应该学的节点 ID（用作缓存 key）"""
    learner = profile.model_dump()
    direction = resolve_direction(learner, profile.target_algorithm)
    full_path = build_path_for_direction(direction)
    mastered = infer_mastered_nodes(learner, learner.get("current_level", "beginner_plus"))
    return recommend_current_node(full_path, mastered)


@router.post("/run")
def generate_resources(profile: LearnerProfile, db: DbSession = Depends(get_db)) -> dict:
    current_node = _compute_current_node(profile)

    # ===== 缓存查询：同一学习者 + 同一关卡节点，直接返回已有结果 =====
    cached = db.query(Session).filter(
        Session.learner_id == profile.learner_id,
        Session.target_node == current_node,
        Session.generated_resources.isnot(None)
    ).order_by(Session.created_at.desc()).first()

    if cached:
        return {
            "session_id": cached.id,
            "generated_resources": cached.generated_resources,
            "diagnosis": cached.diagnosis_summary,
            "evaluation": cached.evaluation,
            "cached": True,
        }

    # ===== 无缓存，走完整 Agent 流水线 =====
    session_in = SessionCreate(
        learner_id=profile.learner_id,
        target_algorithm=profile.target_algorithm
    )
    db_session = session_service.create_session(db, session_in)

    state = run_workflow(profile)

    db_session.generated_resources = state.generated_resources
    db_session.target_node = current_node
    if state.diagnosis:
        db_session.diagnosis_summary = state.diagnosis.model_dump()
    db.commit()

    res = state.model_dump()
    res["session_id"] = db_session.id
    res["cached"] = False
    return res
