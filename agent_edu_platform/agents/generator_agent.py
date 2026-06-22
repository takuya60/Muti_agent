import json
import logging
from typing import Optional
from openai import OpenAI
from backend.config import settings
from schemas.agent_state_schema import WorkflowState
from schemas.resource_schema import CodeStep, CommonError, GeneratedResources, LessonModule, QuizItem
from agents.path_planner import build_learning_plan

logger = logging.getLogger(__name__)

# 中文算法名 → 知识图谱英文 node id 映射
ALGO_NAME_MAP: dict[str, str] = {
    "逻辑回归": "logistic_regression",
    "决策树": "decision_tree",
    "随机森林": "random_forest",
    "支持向量机": "svm",
    "KNN": "knn",
    "朴素贝叶斯": "naive_bayes",
    "线性回归": "linear_regression",
    "无监督学习": "unsupervised_learning",
    "深度学习入门": "deep_learning_intro",
}

SKILL_NODE_MAP: dict[str, str] = {
    "Python基础": "python_basics",
    "Python 基础": "python_basics",
    "Python 基础语法": "python_basics",
    "Numpy/Pandas": "pandas_basics",
    "NumPy": "numpy_basics",
    "Pandas": "pandas_basics",
    "微积分": "calculus",
    "线性代数": "linear_algebra",
    "概率论": "probability",
    "逻辑回归": "logistic_regression",
    "深度学习": "logistic_regression",
}

LEVEL_MASTERED_NODES: dict[str, list[str]] = {
    "beginner": [],
    "beginner_plus": ["python_basics"],
    "intermediate": ["python_basics", "numpy_basics", "pandas_basics", "train_test_split"],
    "advanced": ["python_basics", "numpy_basics", "pandas_basics", "linear_algebra", "probability", "train_test_split", "sigmoid_function"],
}

BASE_PATH_TEMPLATES: dict[str, list[str]] = {
    "logistic_regression": [
        "ml_task_framing",
        "tabular_data_understanding",
        "missing_value_handling",
        "categorical_encoding",
        "feature_scaling",
        "train_validation_test_split",
        "sklearn_workflow",
        "sigmoid_function",
        "cross_entropy_loss",
        "logistic_regression",
        "model_evaluation_metrics",
        "confusion_matrix",
        "precision_recall_f1",
        "roc_auc_pr_curve",
        "cross_validation",
        "regularization",
    ],
    "decision_tree": [
        "ml_task_framing",
        "tabular_data_understanding",
        "missing_value_handling",
        "categorical_encoding",
        "train_validation_test_split",
        "sklearn_workflow",
        "decision_tree",
        "tree_pruning",
        "model_evaluation_metrics",
        "confusion_matrix",
        "cross_validation",
        "random_forest",
        "gradient_boosting",
    ],
    "linear_regression": [
        "ml_task_framing",
        "tabular_data_understanding",
        "missing_value_handling",
        "outlier_handling",
        "feature_engineering",
        "train_validation_test_split",
        "sklearn_workflow",
        "linear_regression",
        "regression_metrics",
        "polynomial_regression",
        "ridge_lasso",
        "cross_validation",
        "learning_validation_curve",
    ],
    "unsupervised_learning": [
        "ml_task_framing",
        "tabular_data_understanding",
        "feature_scaling",
        "pca_dimensionality_reduction",
        "kmeans_clustering",
        "clustering_evaluation",
        "dbscan_clustering",
    ],
    "deep_learning_intro": [
        "ml_task_framing",
        "numpy_basics",
        "feature_scaling",
        "neural_network_intro",
        "forward_backward_propagation",
        "activation_functions",
        "keras_sequential_intro",
        "deep_learning_regularization",
    ],
}


def run_generator_agent(state: WorkflowState) -> WorkflowState:
    diagnosis = state.diagnosis
    level = diagnosis.recommended_level if diagnosis else "beginner_plus"
    evidence_titles = [item.title for item in state.retrieved_knowledge]
    evidence_points = []
    for item in state.retrieved_knowledge:
        evidence_points.extend(item.knowledge_points)

    # Try LLM generation first
    generation_error = ""
    resources = _llm_generation(state, level, evidence_titles, evidence_points)
    
    if resources is None:
        # 记录 fallback 事件
        generation_error = getattr(_llm_generation, "_last_error", "LLM 未配置或调用失败")
        logger.warning(f"LLM 生成失败，降级为 fallback 模式: {generation_error}")
        state.agent_events.append({
            "agent": "资源生成 Agent",
            "status": "fallback",
            "summary": f"LLM 生成失败，使用 fallback 模板: {generation_error}",
        })
        resources = _fallback_generation(state, level, evidence_titles, evidence_points)
        resources.generation_mode = "fallback"
        resources.generation_error = generation_error
    else:
        resources.generation_mode = "llm"

    if evidence_points and len(resources.learning_path) > 0:
        if not any("对齐知识点" in step for step in resources.learning_path):
            resources.learning_path.insert(1, f"对齐知识点：{', '.join(dict.fromkeys(evidence_points[:4]))}")

    resources.final_target = resources.final_target or state.target_algorithm
    _enrich_resources(resources, state, level)

    state.generated_resources = resources.model_dump()
    retry_info = f" (第 {state.retry_count} 次重试)" if state.retry_count > 0 else ""
    state.agent_events.append({
        "agent": "资源生成 Agent",
        "status": "completed",
        "summary": f"[{resources.generation_mode}] 生成 {resources.title}{retry_info}，包含讲义、实操指南和分阶测试题",
    })
    return state

from knowledge_graph.graph_builder import KnowledgeGraphManager

def _llm_generation(state: WorkflowState, level: str, evidence_titles: list, evidence_points: list) -> Optional[GeneratedResources]:
    api_key = settings.DEEPSEEK_API_KEY
    base_url = settings.DEEPSEEK_BASE_URL
    model_name = settings.DEEPSEEK_MODEL
    
    if not api_key:
        _llm_generation._last_error = "DEEPSEEK_API_KEY 未配置（为空）"
        logger.error(_llm_generation._last_error)
        return None

    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 结合知识图谱和学习者画像规划“共同基础 + 分支”路径
    kg = KnowledgeGraphManager()
    learner = state.learner_profile
    profile_level = learner.get("current_level", level)
    plan = build_learning_plan(learner, state.target_algorithm, kg)
    target_algo = plan.final_target

    logger.info(
        "路径规划: direction='%s', current='%s', total=%s",
        plan.direction,
        plan.current_node,
        plan.total_steps,
    )

    current_focus = plan.current_node
    full_path = plan.full_path
    current_focus_name = plan.current_name
    path_names = plan.path_names
    current_step_index = plan.current_step_index
    total_steps = plan.total_steps
    next_focus_name = plan.next_name

    learner = state.learner_profile
    background = learner.get("background", "未提供")
    goal = learner.get("goal", "未提供")
    preferred_style = learner.get("preferred_style", "案例驱动")
    known_skills = learner.get("known_skills", [])
    weak_points = state.diagnosis.weak_points if state.diagnosis else learner.get("weak_points", [])
    test_scores = learner.get("test_scores", {})
    attention_span = learner.get("attention_span_minutes", 30)

    system_prompt = "你是一个经验丰富的机器学习讲师。你的任务是根据学习者画像、诊断结果、知识图谱路径和检索证据，只生成 Markdown 格式的个性化讲义正文。不要输出 JSON。"

    user_prompt = f"""
请只生成 Markdown 讲义正文，不要返回 JSON，不要使用 Markdown 代码围栏包裹全文。

# 生成背景

- 最终学习目标：{target_algo}
- 当前关卡：{current_focus_name}
- 学习进度：第 {current_step_index} / {total_steps} 关
- 下一关预告：{next_focus_name or '暂无，当前已接近终点'}
- 完整学习路径：{' -> '.join(path_names)}
- 推荐原因：{plan.recommended_reason}

# 学习者画像

- 背景：{background}
- 学习目标：{goal}
- 偏好风格：{preferred_style}
- 已知技能：{', '.join(known_skills) if known_skills else '暂无'}
- 薄弱点：{', '.join(weak_points) if weak_points else '暂无明显薄弱点'}
- 测评分数：{json.dumps(test_scores, ensure_ascii=False)}
- 推荐级别：{level}
- 单次专注时长：{attention_span} 分钟

# 参考资料

- 资料来源：{', '.join(evidence_titles) if evidence_titles else '无'}
- 参考知识点：{', '.join(dict.fromkeys(evidence_points)) if evidence_points else '无'}

# 讲义要求

请围绕“{current_focus_name}”生成 1000 到 1500 字的个性化讲义，必须包含以下 Markdown 小节：

## 为什么学这一关
说明这一关在当前学习路径里的位置，以及它如何服务最终目标。

## 核心概念
用适合该学习者基础的方式解释当前知识点。

## 直觉类比
如果学习者偏基础或数学较弱，多用生活化类比；如果学习者基础较强，可以更精炼。

## 必要原理
根据学习者的数学基础决定公式深度。数学弱则少公式，数学强则可以加入必要公式。

## 项目实操中的作用
结合一个小型机器学习项目解释这个知识点如何影响后续数据处理、模型训练或评估。

## 常见误区
列出 3 个初学者容易犯的错误，并说明如何避免。

## 本关小结
用 3 到 5 条要点总结用户学完后应该掌握什么。

要求：
1. 必须明显体现学习者画像差异，不要写成通用模板。
2. 可以使用 Markdown 标题、列表、表格、公式。
3. 不要生成代码练习和测验，它们由后端结构化生成。
4. 不要输出 JSON。
"""
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            timeout=90.0
        )
        theory_note = response.choices[0].message.content.strip()
        if not theory_note:
            raise ValueError("LLM 返回空讲义")

        result = _build_resources_from_markdown(
            theory_note=theory_note,
            level=level,
            plan=plan,
            evidence_titles=evidence_titles,
        )
        logger.info(f"LLM Markdown 讲义生成成功: {result.title}")
        return result
    except Exception as e:
        error_msg = f"LLM 调用异常: {type(e).__name__}: {e}"
        _llm_generation._last_error = error_msg
        logger.error(error_msg)
        state.agent_events.append({
            "agent": "资源生成 Agent",
            "status": "llm_call_error",
            "summary": error_msg,
        })
        return None


def _build_resources_from_markdown(
    *,
    theory_note: str,
    level: str,
    plan,
    evidence_titles: list[str],
) -> GeneratedResources:
    return GeneratedResources(
        title=f"{plan.current_name} 个性化实训讲义",
        learner_level=level,
        theory_note=theory_note,
        dataset_instruction=_dataset_instruction_for(plan.current_name),
        practice_guide=[CodeStep(**step) for step in _default_practice_guide(plan.current_name)],
        graded_quiz=[QuizItem(**item) for item in _default_quiz(plan.current_name)],
        learning_path=plan.path_names,
        learning_path_nodes=plan.full_path,
        citations=evidence_titles,
        final_target=plan.final_target,
        current_focus=plan.current_name,
        current_focus_id=plan.current_node,
        current_step_index=plan.current_step_index,
        total_steps=plan.total_steps,
        next_focus=plan.next_name,
        current_stage=plan.current_stage,
        current_branch=plan.current_branch,
        recommended_reason=plan.recommended_reason,
    )


def _dataset_instruction_for(focus_name: str) -> str:
    return (
        f"本关围绕 **{focus_name}** 设计一个小型表格数据实训。"
        "你可以使用任意包含特征列和目标列的 CSV 数据，先观察字段含义和缺失情况，"
        "再完成训练/测试划分、必要预处理、基线模型训练和指标评估。"
        "重点不是追求高分，而是理解当前知识点在完整机器学习流程中的位置。"
    )


def _default_practice_guide(focus_name: str) -> list[dict[str, str]]:
    return [
        {
            "step_name": "读取数据并查看结构",
            "python_code": "import pandas as pd\n\ndf = pd.read_csv('data.csv')\nprint(df.head())\nprint(df.info())",
            "explanation": f"先看清数据列、缺失值和类型，再讨论 {focus_name} 如何影响建模。",
        },
        {
            "step_name": "划分训练集和测试集",
            "python_code": "from sklearn.model_selection import train_test_split\n\nX = df.drop(columns=['target'])\ny = df['target']\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)",
            "explanation": "先划分数据可以减少数据泄露，让测试集更接近真实未知样本。",
        },
        {
            "step_name": "训练并评估基线模型",
            "python_code": "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score\n\npipe = Pipeline([('scaler', StandardScaler()), ('model', LogisticRegression(max_iter=1000))])\npipe.fit(X_train, y_train)\nprint(accuracy_score(y_test, pipe.predict(X_test)))",
            "explanation": "用 Pipeline 串联预处理和模型训练，便于后续替换模型或加入交叉验证。",
        },
    ]


def _default_quiz(focus_name: str) -> list[dict[str, str]]:
    return [
        {"level": "基础", "question": f"{focus_name} 主要解决什么问题？", "answer": "解释当前知识点在数据、模型或评估流程中的作用。", "explanation": "先把作用讲清楚，比机械记代码更重要。"},
        {"level": "标准", "question": f"如果忽略 {focus_name}，模型训练可能出现什么问题？", "answer": "可能导致训练流程不完整、评估失真或模型泛化变差。", "explanation": "机器学习流程中的每一步都会影响最终评估可信度。"},
        {"level": "进阶", "question": f"如何在一个小项目中验证 {focus_name} 的效果？", "answer": "可以设置对照实验，比较处理前后的验证集指标和错误类型。", "explanation": "通过实验比较，而不是只凭直觉判断改动是否有效。"},
    ]


def _enrich_resources(resources: GeneratedResources, state: WorkflowState, level: str) -> None:
    kg = KnowledgeGraphManager()
    plan = build_learning_plan(state.learner_profile, state.target_algorithm, kg)

    resources.final_target = plan.final_target
    resources.learning_path = plan.path_names
    resources.learning_path_nodes = plan.full_path
    resources.current_focus = plan.current_name
    resources.current_focus_id = plan.current_node
    resources.current_step_index = plan.current_step_index
    resources.total_steps = plan.total_steps
    resources.next_focus = plan.next_name
    resources.current_stage = plan.current_stage
    resources.current_branch = plan.current_branch
    resources.recommended_reason = plan.recommended_reason
    resources.available_branches = plan.available_branches

    if not resources.lesson_modules:
        resources.lesson_modules = _build_lesson_modules(resources)
    if not resources.common_errors:
        resources.common_errors = _build_common_errors(plan.current_node)
    for step in resources.practice_guide:
        if not step.common_errors:
            step.common_errors = _build_code_common_errors()
    resources.agent_trace.steps = [
        {
            "agent": "画像诊断 Agent",
            "title": "分析学习基础",
            "status": "completed",
            "summary": state.agent_events[0].get("summary", "完成学习者画像诊断") if state.agent_events else "完成学习者画像诊断",
            "details": state.diagnosis.weak_points if state.diagnosis else [],
        },
        {
            "agent": "路径规划 Agent",
            "title": "匹配知识图谱路径",
            "status": "completed",
            "summary": plan.recommended_reason,
            "details": [f"当前阶段：{plan.current_stage}", f"当前分支：{plan.current_branch}", f"下一关：{plan.next_name or '暂无'}"],
        },
        {
            "agent": "知识检索 Agent",
            "title": "查找知识库资料",
            "status": "completed",
            "summary": f"检索到 {len(state.retrieved_knowledge)} 条知识库证据",
            "details": [item.title for item in state.retrieved_knowledge[:6]],
        },
        {
            "agent": "资源生成 Agent",
            "title": "生成讲义、代码和测验",
            "status": resources.generation_mode,
            "summary": f"生成模式：{resources.generation_mode}，难度：{level}",
            "details": [resources.title],
        },
        {
            "agent": "审核纠偏 Agent",
            "title": "检查内容质量",
            "status": "completed" if state.review_passed else "needs_review",
            "summary": state.reviewer_feedback or "等待审核结果",
            "details": ["结构完整性", "引用来源", "数据泄露风险", "难度匹配"],
        },
        {
            "agent": "反馈规划 Agent",
            "title": "规划下一步",
            "status": "completed",
            "summary": (state.feedback_decision or {}).get("next_action", "保持当前路径，完成后进入下一关"),
            "details": [f"下一关：{plan.next_name or '当前分支已完成'}"],
        },
    ]
    resources.learning_report = {
        "stage": plan.current_stage,
        "completed_nodes": state.learner_profile.get("mastered_points", []),
        "strengths": state.diagnosis.strengths if state.diagnosis else [],
        "weak_points": state.diagnosis.weak_points if state.diagnosis else [],
        "next_recommendation": plan.recommended_reason,
    }


def _build_lesson_modules(resources: GeneratedResources) -> list[LessonModule]:
    return [
        LessonModule(
            title="为什么学这一关",
            type="why",
            content=resources.recommended_reason or "这一关是后续学习路径中的关键节点，完成后可以更稳地进入下一步。",
            default_open=True,
        ),
        LessonModule(
            title="核心概念讲义",
            type="concept",
            content=resources.theory_note,
            default_open=True,
        ),
        LessonModule(
            title="数据与任务说明",
            type="dataset",
            content=resources.dataset_instruction,
        ),
        LessonModule(
            title="小结与下一步",
            type="summary",
            content=f"完成本关后，建议进入：{resources.next_focus or '阶段复盘'}。",
        ),
    ]


def _build_common_errors(current_node: str) -> list[CommonError]:
    base_errors = [
        CommonError(
            error="数据泄露",
            cause="在划分训练集和测试集之前，对全量数据进行了 fit、标准化或缺失值统计。",
            fix="先 train_test_split，再只在训练集上 fit 预处理器，并用同一个预处理器 transform 测试集。",
        ),
        CommonError(
            error="只看准确率",
            cause="分类任务中类别不平衡时，accuracy 可能掩盖模型漏判问题。",
            fix="结合混淆矩阵、Precision、Recall、F1 或 ROC-AUC 一起判断。",
        ),
    ]
    if current_node in {"python_basics", "numpy_basics", "pandas_basics"}:
        base_errors.insert(0, CommonError(
            error="代码能复制但不理解变量形状",
            cause="没有确认 DataFrame、特征矩阵和标签向量分别是什么。",
            fix="每一步都打印 shape、列名和前几行，先理解数据再训练模型。",
        ))
    return base_errors


def _build_code_common_errors() -> list[CommonError]:
    return [
        CommonError(
            error="ModuleNotFoundError",
            cause="本地环境没有安装 scikit-learn、pandas 或 numpy。",
            fix="在当前 Python 环境中安装缺失依赖，例如 pip install scikit-learn pandas numpy。",
        ),
        CommonError(
            error="ValueError: Input contains NaN",
            cause="特征中仍然存在缺失值，模型无法直接训练。",
            fix="训练前使用 fillna、SimpleImputer 或删除缺失严重的列。",
        ),
    ]


def _build_learning_path(target_node: str) -> list[str]:
    return list(BASE_PATH_TEMPLATES.get(target_node, BASE_PATH_TEMPLATES["logistic_regression"]))


def _recommend_current_node(target_node: str, mastered_nodes: list[str]) -> str:
    for node in _build_learning_path(target_node):
        if node not in mastered_nodes:
            return node
    return target_node


def _infer_mastered_nodes(learner: dict, profile_level: str) -> list[str]:
    mastered = set(learner.get("mastered_points", []))
    mastered.update(LEVEL_MASTERED_NODES.get(profile_level, []))

    for skill in learner.get("known_skills", []):
        node = SKILL_NODE_MAP.get(skill)
        if node:
            mastered.add(node)

    for node, score in learner.get("knowledge_mastery", {}).items():
        if score >= 0.7:
            mastered.add(node)

    return list(mastered)


# 初始化函数属性
_llm_generation._last_error = ""

def _fallback_generation(state: WorkflowState, level: str, evidence_titles: list, evidence_points: list) -> GeneratedResources:
    if level == "advanced":
        theory = _advanced_theory(state.target_algorithm)
        path = ["快速复盘核心原理", "完成标准训练流程", "加入交叉验证", "分析模型局限并设计改进"]
        practice_guide = [
            CodeStep(
                step_name="加载数据并划分训练/测试集",
                python_code="from sklearn.datasets import load_breast_cancer\nfrom sklearn.model_selection import train_test_split\n\ndata = load_breast_cancer()\nX_train, X_test, y_train, y_test = train_test_split(\n    data.data, data.target, test_size=0.2, random_state=42, stratify=data.target\n)",
                explanation="分层抽样保证类别分布，后续需考虑类别不平衡处理。",
            ),
            CodeStep(
                step_name="Pipeline构建与交叉验证",
                python_code="from sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.model_selection import cross_val_score\n\npipeline = Pipeline([\n    ('scaler', StandardScaler()),\n    ('clf', LogisticRegression(C=0.1, class_weight='balanced', max_iter=1000))\n])\nscores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='f1')\nprint(f'CV F1 Scores: {scores}')",
                explanation="使用Pipeline防止数据泄露，C=0.1增加正则化，class_weight处理可能的不平衡。通过交叉验证评估泛化能力。",
            ),
            CodeStep(
                step_name="最终训练与详细评估",
                python_code="from sklearn.metrics import classification_report, confusion_matrix\n\npipeline.fit(X_train, y_train)\ny_pred = pipeline.predict(X_test)\nprint(confusion_matrix(y_test, y_pred))\nprint(classification_report(y_test, y_pred))",
                explanation="在测试集验证最终效果。",
            ),
        ]
    elif level == "intermediate":
        theory = _intermediate_theory(state.target_algorithm)
        path = ["补齐薄弱知识点", "完成标准实验", "解释评估指标", "尝试参数调整"]
        practice_guide = [
            CodeStep(
                step_name="加载数据并划分训练/测试集",
                python_code="from sklearn.datasets import load_breast_cancer\nfrom sklearn.model_selection import train_test_split\n\ndata = load_breast_cancer()\nX_train, X_test, y_train, y_test = train_test_split(\n    data.data, data.target, test_size=0.2, random_state=42, stratify=data.target\n)",
                explanation="先划分数据，保证测试集模拟真实未知样本；stratify 保持类别比例一致。",
            ),
            CodeStep(
                step_name="标准化与模型训练",
                python_code="from sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\n\nscaler = StandardScaler()\nX_train_scaled = scaler.fit_transform(X_train)\nX_test_scaled = scaler.transform(X_test)\n\nmodel = LogisticRegression(max_iter=1000)\nmodel.fit(X_train_scaled, y_train)",
                explanation="标准化器只能 fit 训练集，再 transform 测试集；逻辑回归通过 fit 学习分类边界。",
            ),
            CodeStep(
                step_name="评估模型效果",
                python_code="from sklearn.metrics import accuracy_score, classification_report, confusion_matrix\n\ny_pred = model.predict(X_test_scaled)\nprint(accuracy_score(y_test, y_pred))\nprint(confusion_matrix(y_test, y_pred))\nprint(classification_report(y_test, y_pred, target_names=data.target_names))",
                explanation="准确率给出总体正确比例，混淆矩阵能看到错分类型，classification_report 展示 precision、recall 和 f1-score。",
            ),
        ]
    else:
        theory = _beginner_theory(state.target_algorithm)
        path = ["理解分类任务", "掌握 Sigmoid 概率输出", "跟随代码完成训练", "用准确率和混淆矩阵评估"]
        practice_guide = [
            CodeStep(
                step_name="加载数据",
                python_code="from sklearn.datasets import load_breast_cancer\nfrom sklearn.model_selection import train_test_split\n\n# 导入内置数据集\ndata = load_breast_cancer()\n# 切分数据，80%训练，20%测试\nX_train, X_test, y_train, y_test = train_test_split(\n    data.data, data.target, test_size=0.2, random_state=42\n)",
                explanation="像考试一样，我们把数据分成平时练习题（训练集）和期末考试题（测试集）。",
            ),
            CodeStep(
                step_name="模型训练",
                python_code="from sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\n\n# 统一特征范围，帮助模型更好学习\nscaler = StandardScaler()\nX_train_scaled = scaler.fit_transform(X_train)\nX_test_scaled = scaler.transform(X_test)\n\n# 创建并训练逻辑回归模型\nmodel = LogisticRegression()\nmodel.fit(X_train_scaled, y_train)",
                explanation="先归一化数据（类似大家在同一个起跑线），然后让模型从练习题里学习规律。",
            ),
            CodeStep(
                step_name="测试效果",
                python_code="from sklearn.metrics import accuracy_score\n\n# 让模型做期末考试题\ny_pred = model.predict(X_test_scaled)\n# 算一算正确率\nacc = accuracy_score(y_test, y_pred)\nprint(f'准确率: {acc}')",
                explanation="预测测试集并对比真实答案，算出准确率。",
            ),
        ]

    path = _fallback_path_for_level(level)
    current_focus = path[0]
    next_focus = path[1] if len(path) > 1 else ""

    resources = GeneratedResources(
        title=f"{current_focus} 个性化闯关资源",
        learner_level=level,
        theory_note=theory,
        dataset_instruction="使用 sklearn 内置 breast_cancer 二分类数据集。特征是肿瘤细胞的统计量，标签表示良性或恶性。先划分训练集和测试集，再只在训练集上拟合标准化器，避免数据泄露。",
        practice_guide=practice_guide,
        graded_quiz=[
            QuizItem(
                level="基础",
                question="为什么不能先对全量数据标准化再划分训练集和测试集？",
                answer="因为测试集信息会泄露到训练过程，导致评估结果虚高。",
                explanation="标准化的均值和方差如果来自全量数据，就包含了测试集分布信息。",
            ),
            QuizItem(
                level="标准",
                question="逻辑回归输出的 0 到 1 之间的数可以怎样理解？",
                answer="可以理解为样本属于正类的概率估计。",
                explanation="Sigmoid 函数把线性打分压缩到 0 到 1 区间。",
            ),
            QuizItem(
                level="进阶",
                question="如果模型召回率很低但准确率较高，训练场景中可能有什么风险？",
                answer="可能漏掉大量真正的正类样本，在医疗、风控等场景会带来严重风险。",
                explanation="准确率可能被多数类掩盖，召回率低说明正类识别不足。",
            ),
        ],
        learning_path=path,
        learning_path_nodes=path,
        citations=evidence_titles,
        final_target=state.target_algorithm,
        current_focus=current_focus,
        current_focus_id=current_focus,
        current_step_index=1,
        total_steps=len(path),
        next_focus=next_focus,
    )
    return resources

def _fallback_path_for_level(level: str) -> list[str]:
    if level == "advanced":
        return ["快速复盘核心原理", "完成标准训练流程", "加入交叉验证", "分析模型局限并设计改进"]
    if level == "intermediate":
        return ["补齐薄弱知识点", "完成标准实验", "解释评估指标", "尝试参数调整"]
    return ["理解分类任务", "掌握 Sigmoid 概率输出", "跟随代码完成训练", "用准确率和混淆矩阵评估"]


def _beginner_theory(algorithm: str) -> str:
    return f"{algorithm}可以先理解成一个概率打分器：模型把多个特征加权求和，再通过 Sigmoid 函数压缩到 0 到 1 之间。数学基础薄弱时，不必先深究推导，重点理解它如何把样本分成两类，以及为什么要用训练集学习参数、用测试集检查泛化效果。"

def _intermediate_theory(algorithm: str) -> str:
    return f"{algorithm}的核心是用线性函数得到打分 $z = w^Tx + b$，再用 Sigmoid 函数 $\\sigma(z)=1/(1+e^{{-z}})$ 转成概率。训练过程会最小化分类损失，使正类样本概率更接近 1，负类样本概率更接近 0。"

def _advanced_theory(algorithm: str) -> str:
    return f"{algorithm}可视为广义线性模型在二分类任务中的典型形式。除了掌握 $\\sigma(w^Tx+b)$ 与交叉熵损失，还应关注正则化、类别不平衡、阈值移动和概率校准对工程效果的影响。"
