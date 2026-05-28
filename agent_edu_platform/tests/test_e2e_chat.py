"""
端到端测试: 验证 generation -> chat 全链路
使用 FastAPI TestClient 无需启动真实服务器
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# 测试用的学习者画像
TEST_PROFILE = {
    "learner_id": "test_e2e_user",
    "name": "测试同学",
    "background": "计算机本科，学过Python",
    "goal": "掌握逻辑回归",
    "target_algorithm": "逻辑回归",
    "preferred_style": "案例驱动",
    "test_scores": {},
    "known_skills": ["python_basics"],
    "weak_points": [],
    "mastered_points": [],
    "current_level": "beginner_plus",
}


def generate_and_assert_session() -> str:
    resp = client.post("/generation/run", json=TEST_PROFILE)
    assert resp.status_code == 200, f"生成接口返回 {resp.status_code}: {resp.text}"

    data = resp.json()
    assert "session_id" in data, f"返回数据中缺少 session_id: {list(data.keys())}"
    assert data["session_id"], "session_id 为空"

    assert "generated_resources" in data, f"返回数据中缺少 generated_resources: {list(data.keys())}"
    resources = data["generated_resources"]
    assert resources is not None, "generated_resources 为 None"
    assert "title" in resources, f"generated_resources 缺少 title: {list(resources.keys())}"
    assert "theory_note" in resources, "generated_resources 缺少 theory_note"
    assert len(resources["theory_note"]) > 20, f"theory_note 太短，疑似未调用 LLM: '{resources['theory_note'][:100]}'"

    if "generation_mode" in resources:
        print(f"[INFO] generation_mode = {resources['generation_mode']}")
        if resources.get("generation_error"):
            print(f"[WARN] generation_error = {resources['generation_error']}")

    return data["session_id"]


def test_generation_returns_session_id_and_resources():
    """测试 /generation/run 返回 session_id 和 generated_resources"""
    generate_and_assert_session()


def test_chat_stream_returns_content():
    """测试 /sessions/{id}/chat/stream 返回非空 SSE 内容"""
    session_id = generate_and_assert_session()
    
    # 发送聊天消息
    chat_resp = client.post(
        f"/sessions/{session_id}/chat/stream",
        json={"role": "user", "content": "什么是逻辑回归？"}
    )
    assert chat_resp.status_code == 200, f"聊天接口返回 {chat_resp.status_code}: {chat_resp.text}"
    
    # 解析 SSE 内容
    body = chat_resp.text
    assert len(body) > 0, "SSE 响应体为空"
    
    import json
    lines = body.strip().split("\n\n")
    contents = []
    for line in lines:
        if line.startswith("data: "):
            payload = json.loads(line[6:])
            if payload.get("content"):
                contents.append(payload["content"])
    
    full_response = "".join(contents)
    print(f"[INFO] AI 回复 ({len(full_response)} 字): {full_response[:200]}...")
    assert len(full_response) > 0, "AI 回复内容为空，LLM 可能未接入"


if __name__ == "__main__":
    print("=== 测试 1: 资源生成 ===")
    sid = test_generation_returns_session_id_and_resources()
    print(f"✅ 通过, session_id = {sid}")
    
    print("\n=== 测试 2: 聊天流 ===")
    test_chat_stream_returns_content()
    print("✅ 通过")
