from fastapi import FastAPI
import backend.config # Ensure env vars are loaded

from backend.api.evaluation import router as evaluation_router
from backend.api.feedback import router as feedback_router
from backend.api.generation import router as generation_router
from backend.api.learner import router as learner_router
from backend.api.session import router as session_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AgentEdu 多智能体个性化实训平台", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.chat import router as chat_router
from backend.api.learning_tree import router as learning_tree_router

app.include_router(learner_router)
app.include_router(session_router)
app.include_router(generation_router)
app.include_router(feedback_router)
app.include_router(evaluation_router)
app.include_router(chat_router)
app.include_router(learning_tree_router)

# 启动时自动建表
from backend.database import engine, Base
import backend.models  # noqa: F401 — 确保所有 ORM 模型已注册到 Base.metadata

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
