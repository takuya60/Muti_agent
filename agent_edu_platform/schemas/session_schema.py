from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List

class SessionCreate(BaseModel):
    learner_id: str
    target_algorithm: str
    
class SessionResponse(BaseModel):
    id: str
    learner_id: str
    target_algorithm: str
    current_phase: str
    diagnosis_summary: Optional[Dict[str, Any]] = None
    generated_resources: Optional[Dict[str, Any]] = None
    evaluation: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)

class MessageCreate(BaseModel):
    role: str
    content: str
    agent_name: Optional[str] = None
    
class MessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    agent_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
