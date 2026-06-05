import requests
import json
import time

profile = {
    "learner_id": "test_user_002",
    "name": "Test",
    "goal": "Test Streaming",
    "target_algorithm": "svm"
}

print("Starting request...")
start = time.time()
with requests.post("http://127.0.0.1:8001/generation/stream", json=profile, stream=True) as r:
    for line in r.iter_lines():
        if line:
            print(f"[{time.time() - start:.2f}s] {line.decode('utf-8')}")
