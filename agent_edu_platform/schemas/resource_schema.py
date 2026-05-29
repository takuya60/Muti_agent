from pydantic import BaseModel, Field


class CommonError(BaseModel):
    error: str
    cause: str = ""
    fix: str = ""


class CodeStep(BaseModel):
    step_name: str
    python_code: str
    explanation: str
    expected_output: str = ""
    common_errors: list[CommonError] = Field(default_factory=list)


class QuizItem(BaseModel):
    question: str
    level: str = Field(description="基础 / 标准 / 进阶")
    answer: str
    explanation: str


class LessonModule(BaseModel):
    title: str
    type: str = "concept"
    content: str
    default_open: bool = False


class CompletionRequirement(BaseModel):
    read_required: bool = True
    code_required: bool = True
    quiz_required: bool = True
    min_quiz_score: int = 60


class LearningBranch(BaseModel):
    id: str
    title: str
    description: str = ""
    progress: float = 0.0
    recommended: bool = False
    locked_reason: str = ""


class AgentTraceStep(BaseModel):
    agent: str
    title: str
    status: str = "completed"
    summary: str
    details: list[str] = Field(default_factory=list)


class AgentTrace(BaseModel):
    steps: list[AgentTraceStep] = Field(default_factory=list)


class GeneratedResources(BaseModel):
    title: str
    learner_level: str
    theory_note: str
    dataset_instruction: str
    practice_guide: list[CodeStep]
    graded_quiz: list[QuizItem]
    learning_path: list[str]
    learning_path_nodes: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    final_target: str = ""
    current_focus: str = ""
    current_focus_id: str = ""
    current_step_index: int = 1
    total_steps: int = 1
    next_focus: str = ""
    current_stage: str = ""
    current_branch: str = ""
    recommended_reason: str = ""
    lesson_modules: list[LessonModule] = Field(default_factory=list)
    common_errors: list[CommonError] = Field(default_factory=list)
    completion_requirements: CompletionRequirement = Field(default_factory=CompletionRequirement)
    available_branches: list[LearningBranch] = Field(default_factory=list)
    agent_trace: AgentTrace = Field(default_factory=AgentTrace)
    learning_report: dict = Field(default_factory=dict)
    # 调试/可观测字段
    generation_mode: str = "unknown"   # "llm" | "fallback"
    generation_error: str = ""         # LLM 失败时记录原因
