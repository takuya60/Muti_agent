from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json
import asyncio
from sqlalchemy.orm import Session as DbSession
from backend.database import get_db
from backend.services import session_service
from backend.models import Session
from schemas.session_schema import SessionCreate

from agents.workflow import run_workflow, _GRAPH
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

@router.post("/stream")
def generate_resources_stream(profile: LearnerProfile, db: DbSession = Depends(get_db)):
    current_node = _compute_current_node(profile)

    # ===== 缓存查询 =====
    cached = db.query(Session).filter(
        Session.learner_id == profile.learner_id,
        Session.target_node == current_node,
        Session.generated_resources.isnot(None)
    ).order_by(Session.created_at.desc()).first()

    async def event_generator():
        if cached:
            # 伪造一个流式反馈以防前端 UI 突变
            msg = {"node": "cache", "status": "success", "message": "发现本地缓存，直接加载..."}
            yield f"data: {json.dumps(msg)}\n\n"
            await asyncio.sleep(0.5)

            final_data = {
                "session_id": cached.id,
                "generated_resources": cached.generated_resources,
                "diagnosis": cached.diagnosis_summary,
                "evaluation": cached.evaluation,
                "cached": True,
                "is_complete": True
            }
            yield f"data: {json.dumps(final_data)}\n\n"
            return

        # ===== 无缓存，走完整 Agent 流水线 =====
        session_in = SessionCreate(
            learner_id=profile.learner_id,
            target_algorithm=profile.target_algorithm
        )
        db_session = session_service.create_session(db, session_in)

        initial_state = {
            "learner_id": profile.learner_id,
            "learner_profile": profile.model_dump(),
            "target_algorithm": profile.target_algorithm,
            "review_passed": False,
            "retry_count": 0,
            "agent_events": [],
            "feedback_decision": None,
            "reviewer_feedback": "",
            "generated_resources": None,
            "evaluation": None,
            "quiz_accuracy": None,
            "learner_feedback": "",
        }

        final_state = None
        # LangGraph Stream
        try:
            # 注意: _GRAPH.stream 是同步的，在 FastAPI 中 StreamingResponse 允许同步或异步 generator。
            # 这里我们使用异步 generator 并把同步的 stream 放到迭代里。为了防止阻塞，可以考虑 to_thread，但由于是本地演示，直接跑也可以。
            for output in _GRAPH.stream(initial_state):
                for node_name, state_update in output.items():
                    msg = {"node": node_name, "status": "running", "message": f"Agent [{node_name}] 执行完毕..."}
                    if node_name == "diagnose_agent":
                        msg["message"] = "🧠 画像诊断完成，正在规划路径..."
                    elif node_name == "path_planner":
                        msg["message"] = "🗺️ 路径规划完成，正在检索底层知识库..."
                    elif node_name == "retrieval_agent":
                        msg["message"] = "📚 RAG 检索完成，开始生成教学内容..."
                    elif node_name == "generator_agent":
                        msg["message"] = "✨ 核心内容生成完毕，正在进行交叉审查..."
                    elif node_name == "review_agent":
                        passed = state_update.get("review_passed", False)
                        if passed:
                            msg["message"] = "✅ 质量审查通过！"
                        else:
                            msg["status"] = "warning"
                            msg["message"] = "⚠️ 审查发现问题，打回重做中..."

                    yield f"data: {json.dumps(msg)}\n\n"
                    # 更新 final_state，因为 stream 中每个块只包含增量，不过我们也可以从最后一个块拿。
                    # 其实 LangGraph stream 也会给出更新，我们可以最后自己构造或从 output 提取。
                    # 但最好是获取完整的 final state，实际上 LangGraph 的 state_update 是增量。
                    # 为了简化，我们只在最后自己做一次查询或从 db 里写。
                    
                    if state_update:
                        if final_state is None:
                            final_state = initial_state.copy()
                        final_state.update(state_update)

                await asyncio.sleep(0.1)
                
        except Exception as e:
            err = {"node": "error", "status": "error", "message": f"执行出错: {str(e)}"}
            yield f"data: {json.dumps(err)}\n\n"
            return
            
        # 存入数据库
        if final_state and "generated_resources" in final_state and final_state["generated_resources"]:
            db_session.generated_resources = final_state["generated_resources"]
            db_session.target_node = current_node
            if final_state.get("diagnosis"):
                # 如果是 pydantic model 就要 model_dump，如果是 dict 就直接赋值
                diag = final_state["diagnosis"]
                db_session.diagnosis_summary = diag.model_dump() if hasattr(diag, 'model_dump') else diag
            db.commit()

            final_data = {
                "session_id": db_session.id,
                "generated_resources": final_state["generated_resources"],
                "diagnosis": db_session.diagnosis_summary,
                "evaluation": final_state.get("evaluation"),
                "cached": False,
                "is_complete": True
            }
            yield f"data: {json.dumps(final_data)}\n\n"
        else:
            err = {"node": "error", "status": "error", "message": "生成失败，未获得资源"}
            yield f"data: {json.dumps(err)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
