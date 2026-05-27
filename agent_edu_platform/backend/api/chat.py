from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services import session_service
from schemas.session_schema import MessageCreate, MessageResponse
from schemas.agent_state_schema import ChatState
from agents.chat_graph import run_chat_workflow

router = APIRouter(prefix="/sessions", tags=["chat"])

@router.post("/{session_id}/chat", response_model=MessageResponse)
def handle_chat(session_id: str, message: dict, db: Session = Depends(get_db)):
    """处理用户提问，触发 Chat Graph"""
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    user_msg_content = message.get("content", "")
    if not user_msg_content:
        raise HTTPException(status_code=400, detail="Message content is empty")

    # 1. 保存用户消息
    user_msg = MessageCreate(role="user", content=user_msg_content)
    session_service.add_message(db, session_id, user_msg)
    
    # 2. 提取最近的历史记录（过滤掉系统事件等噪音）
    db_messages = session_service.get_session_messages(db, session_id)
    chat_history = []
    for m in db_messages:
        # 只保留 user 和 assistant (即系统回答)
        if m.role in ("user", "system"):
            if m.content != user_msg_content: # 排除刚插入的当前句
                chat_history.append({"role": m.role, "content": m.content})
    
    # 3. 构建 ChatState，注入生成的讲义作为 Context
    state = ChatState(
        session_id=session_id,
        user_message=user_msg_content,
        chat_history=chat_history,
        current_resource_context=session.generated_resources if session.generated_resources else {}
    )
    
    # 4. 运行 LangGraph (Router -> Answer / Off-topic)
    final_state = run_chat_workflow(state)
    
    # 5. 保存 Agent 响应
    agent_msg = MessageCreate(role="system", content=final_state.agent_response, agent_name=final_state.next_node)
    saved_msg = session_service.add_message(db, session_id, agent_msg)
    
    return saved_msg

from fastapi.responses import StreamingResponse
import json
from agents.router_agent import run_router_agent
from agents.answer_agent import stream_answer_agent

@router.post("/{session_id}/chat/stream")
def handle_chat_stream(session_id: str, message: dict, db: Session = Depends(get_db)):
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    user_msg_content = message.get("content", "")
    if not user_msg_content:
        raise HTTPException(status_code=400, detail="Message content is empty")

    user_msg = MessageCreate(role="user", content=user_msg_content)
    session_service.add_message(db, session_id, user_msg)
    
    db_messages = session_service.get_session_messages(db, session_id)
    chat_history = []
    for m in db_messages:
        if m.role in ("user", "system") and m.content != user_msg_content:
            chat_history.append({"role": m.role, "content": m.content})
    
    state = ChatState(
        session_id=session_id,
        user_message=user_msg_content,
        chat_history=chat_history,
        current_resource_context=session.generated_resources if session.generated_resources else {}
    )
    
    state = run_router_agent(state)
    
    def event_generator():
        full_response = ""
        if state.next_node == "off_topic":
            full_response = "我是一个专业的机器学习实训导师，你的问题与当前学习的内容无关，请回到课程内容。"
            yield f"data: {json.dumps({'content': full_response, 'done': False})}\n\n"
        else:
            for chunk in stream_answer_agent(state):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
                
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        
        agent_msg = MessageCreate(role="system", content=full_response, agent_name=state.next_node)
        session_service.add_message(db, session_id, agent_msg)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
