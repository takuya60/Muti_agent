from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from backend.database import Base

class Learner(Base):
    """学习者表：跨会话持久存储画像与能力雷达"""
    __tablename__ = "learners"
    
    id = Column(String, primary_key=True, index=True) # learner_id
    name = Column(String, nullable=False)
    background = Column(Text)
    goal = Column(Text)
    preferred_style = Column(String, default="案例驱动")
    test_scores = Column(JSON, default={})
    known_skills = Column(JSON, default=[])
    weak_points = Column(JSON, default=[])
    mastered_points = Column(JSON, default=[])        # 跨会话累积掌握的知识点
    current_level = Column(String, default="beginner_plus")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Session(Base):
    """学习会话表：一次完整的学习交互生命周期"""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, index=True) # session_id (UUID)
    learner_id = Column(String, ForeignKey("learners.id"))
    target_algorithm = Column(String)
    current_phase = Column(String, default="init")    # init, diagnosing, learning, quizzing, completed
    
    # 存放诊断结果、生成的资料、评测快照等
    diagnosis_summary = Column(JSON, nullable=True)
    generated_resources = Column(JSON, nullable=True)
    evaluation = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Message(Base):
    """对话消息表：持久化所有的交互历史，脱离 State 以防内存爆炸"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    role = Column(String, nullable=False)             # 'user', 'assistant', 'system', 'agent_event'
    content = Column(Text, nullable=False)
    agent_name = Column(String, nullable=True)        # 记录是哪个 Agent 触发的事件
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class QuizAttempt(Base):
    """答题记录表：用于更新画像并进行评测追踪"""
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    learner_id = Column(String, ForeignKey("learners.id"))
    question = Column(Text, nullable=False)
    learner_answer = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    knowledge_point = Column(String, nullable=True)   # 对应考查的知识点
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
