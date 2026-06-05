import asyncio
import time
from agents.workflow import _GRAPH

async def test_astream_behavior():
    initial_state = {
        "learner_id": "test_user_001",
        "learner_profile": {
            "learner_id": "test_user_001",
            "name": "Test User",
            "goal": "Test stream",
            "target_algorithm": "svm"
        },
        "target_algorithm": "svm",
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
    
    print(f"[{time.time()}] Starting astream...")
    start_time = time.time()
    try:
        async for output in _GRAPH.astream(initial_state):
            for node_name, state_update in output.items():
                print(f"[{time.time() - start_time:.2f}s] Yielded from node: {node_name}")
    except Exception as e:
        print(f"Error during astream: {e}")

if __name__ == "__main__":
    asyncio.run(test_astream_behavior())
