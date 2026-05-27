from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_session_lifecycle():
    # 1. 验证创建 session
    response = client.post("/sessions", json={
        "learner_id": "beginner_001",
        "target_algorithm": "logistic_regression"
    })
    assert response.status_code == 200
    session_data = response.json()
    assert "id" in session_data
    assert session_data["learner_id"] == "beginner_001"
    assert session_data["current_phase"] == "init"
    
    session_id = session_data["id"]
    
    # 2. 验证获取 session
    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["id"] == session_id
    
    # 3. 验证发送消息
    response = client.post(f"/sessions/{session_id}/messages", json={
        "role": "user",
        "content": "逻辑回归是什么？"
    })
    assert response.status_code == 200
    msg_data = response.json()
    assert msg_data["content"] == "逻辑回归是什么？"
    
    # 4. 验证获取消息列表
    response = client.get(f"/sessions/{session_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"

def test_learner_api_db_integration():
    # 确保 learner 接口现在不报错（前提是 init_db.py 跑过，数据库里有数据）
    response = client.get("/learners/examples")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
