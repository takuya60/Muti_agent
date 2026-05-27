import json
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.workflow import run_workflow
from schemas.learner_schema import LearnerProfile


def run_demo(profile_name: str = "beginner") -> dict:
    profile_path = PROJECT_ROOT / "data" / "learner_profiles" / f"{profile_name}.json"
    profile = LearnerProfile.model_validate_json(profile_path.read_text(encoding="utf-8"))
    state = run_workflow(profile)
    return state.model_dump()


if __name__ == "__main__":
    result = run_demo()
    print(json.dumps(result, ensure_ascii=False, indent=2))
