from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from schemas.session_schema import SessionCreate, SessionResponse, MessageCreate, MessageResponse
from backend.services import session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("", response_model=SessionResponse)
def create_session(session_in: SessionCreate, db: Session = Depends(get_db)):
    return session_service.create_session(db, session_in)

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/{session_id}/messages", response_model=MessageResponse)
def add_message(session_id: str, msg_in: MessageCreate, db: Session = Depends(get_db)):
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_service.add_message(db, session_id, msg_in)

@router.get("/{session_id}/messages", response_model=list[MessageResponse])
def get_messages(session_id: str, db: Session = Depends(get_db)):
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_service.get_session_messages(db, session_id)
