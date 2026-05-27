import uuid
from sqlalchemy.orm import Session
from backend.models import Session as DBSession, Message
from schemas.session_schema import SessionCreate, MessageCreate

def create_session(db: Session, session_in: SessionCreate):
    session_id = str(uuid.uuid4())
    db_session = DBSession(
        id=session_id,
        learner_id=session_in.learner_id,
        target_algorithm=session_in.target_algorithm,
        current_phase="init"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: str):
    return db.query(DBSession).filter(DBSession.id == session_id).first()

def add_message(db: Session, session_id: str, msg_in: MessageCreate):
    db_msg = Message(
        session_id=session_id,
        role=msg_in.role,
        content=msg_in.content,
        agent_name=msg_in.agent_name
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg

def get_session_messages(db: Session, session_id: str):
    return db.query(Message).filter(Message.session_id == session_id).order_by(Message.id.asc()).all()
