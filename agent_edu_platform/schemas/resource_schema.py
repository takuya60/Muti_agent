from pydantic import BaseModel, Field


class CodeStep(BaseModel):
    step_name: str
    python_code: str
    explanation: str


class QuizItem(BaseModel):
    question: str
    level: str = Field(description="基础 / 标准 / 进阶")
    answer: str
    explanation: str


class GeneratedResources(BaseModel):
    title: str
    learner_level: str
    theory_note: str
    dataset_instruction: str
    practice_guide: list[CodeStep]
    graded_quiz: list[QuizItem]
    learning_path: list[str]
    citations: list[str] = Field(default_factory=list)
    final_target: str = ""
    current_focus: str = ""
    current_step_index: int = 1
    total_steps: int = 1
    next_focus: str = ""
    # 调试/可观测字段
    generation_mode: str = "unknown"   # "llm" | "fallback"
    generation_error: str = ""         # LLM 失败时记录原因
