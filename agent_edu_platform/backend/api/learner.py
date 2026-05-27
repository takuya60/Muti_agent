import json
from pathlib import Path

from fastapi import APIRouter

from schemas.learner_schema import LearnerProfile


router = APIRouter(prefix="/learners", tags=["learners"])
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR = PROJECT_ROOT / "data" / "learner_profiles"


@router.get("/examples")
def list_example_profiles() -> list[dict]:
    profiles = []
    for path in sorted(PROFILE_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        profiles.append({
            "profile_name": path.stem,
            "learner_id": data["learner_id"],
            "name": data["name"],
            "goal": data["goal"],
        })
    return profiles


@router.post("/validate")
def validate_profile(profile: LearnerProfile) -> dict:
    return {"valid": True, "profile": profile.model_dump()}
