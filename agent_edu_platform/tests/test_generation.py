import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from schemas.resource_schema import CodeStep, GeneratedResources, QuizItem


def test_generated_resource_schema():
    resource = GeneratedResources(
        title="测试资源",
        learner_level="beginner_plus",
        theory_note="理论讲义",
        dataset_instruction="数据说明",
        practice_guide=[CodeStep(step_name="步骤", python_code="print('ok')", explanation="解释")],
        graded_quiz=[QuizItem(question="问题", level="基础", answer="答案", explanation="解析")],
        learning_path=["第一步"],
        citations=["source"],
    )

    assert resource.title == "测试资源"
