from fastapi import FastAPI

from backend.api.evaluation import router as evaluation_router
from backend.api.feedback import router as feedback_router
from backend.api.generation import router as generation_router
from backend.api.learner import router as learner_router


app = FastAPI(title="AgentEdu 多智能体个性化实训平台", version="0.1.0")

app.include_router(learner_router)
app.include_router(generation_router)
app.include_router(feedback_router)
app.include_router(evaluation_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
