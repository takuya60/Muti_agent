from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from backend.database import get_db
from agents.path_planner import build_learning_tree
from knowledge_graph.graph_builder import KnowledgeGraphManager

router = APIRouter(prefix="/learning-tree", tags=["learning-tree"])

_kg = KnowledgeGraphManager()


class SwitchBranchRequest(BaseModel):
    learner_profile: dict
    target_branch: str
    target_algorithm: str = "由系统推荐"


@router.post("/tree")
def get_learning_tree(learner_profile: dict) -> dict:
    """
    获取完整的树状学习路径。
    前端传入当前学习者画像，后端返回 trunk + branches 的树结构。
    """
    target_algorithm = learner_profile.get("target_algorithm", "由系统推荐")
    tree = build_learning_tree(learner_profile, target_algorithm, _kg)
    return tree


@router.post("/switch-branch")
def switch_branch(req: SwitchBranchRequest) -> dict:
    """
    切换学习分支。
    更新学习者的 target_direction，重新计算当前推荐节点，返回新的树结构。
    """
    profile = req.learner_profile
    profile["target_direction"] = req.target_branch
    tree = build_learning_tree(profile, req.target_algorithm, _kg)
    return tree
