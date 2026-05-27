import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.workflow import run_workflow
from schemas.learner_schema import LearnerProfile


def test_workflow_generates_complete_resources():
    profile_path = PROJECT_ROOT / "data" / "learner_profiles" / "beginner.json"
    profile = LearnerProfile.model_validate_json(profile_path.read_text(encoding="utf-8"))

    state = run_workflow(profile)

    assert state.review_passed is True
    assert state.generated_resources is not None
    assert len(state.generated_resources["practice_guide"]) >= 3
    assert len(state.generated_resources["graded_quiz"]) >= 3
    assert state.evaluation["knowledge_coverage"] >= 0.8
