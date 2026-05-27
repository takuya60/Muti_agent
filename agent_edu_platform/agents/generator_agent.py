import os
import json
from typing import Optional
from openai import OpenAI
from schemas.agent_state_schema import WorkflowState
from schemas.resource_schema import CodeStep, GeneratedResources, QuizItem

def run_generator_agent(state: WorkflowState) -> WorkflowState:
    diagnosis = state.diagnosis
    level = diagnosis.recommended_level if diagnosis else "beginner_plus"
    evidence_titles = [item.title for item in state.retrieved_knowledge]
    evidence_points = []
    for item in state.retrieved_knowledge:
        evidence_points.extend(item.knowledge_points)

    # Try LLM generation first
    resources = _llm_generation(state, level, evidence_titles, evidence_points)
    
    if resources is None:
        resources = _fallback_generation(state, level, evidence_titles, evidence_points)

    if evidence_points and len(resources.learning_path) > 0:
        if not any("对齐知识点" in step for step in resources.learning_path):
            resources.learning_path.insert(1, f"对齐知识点：{', '.join(dict.fromkeys(evidence_points[:4]))}")

    state.generated_resources = resources.model_dump()
    state.agent_events.append({
        "agent": "资源生成 Agent",
        "status": "completed",
        "summary": f"生成 {resources.title}，包含讲义、实操指南和分阶测试题",
    })
    return state

from knowledge_graph.graph_builder import KnowledgeGraphManager

def _llm_generation(state: WorkflowState, level: str, evidence_titles: list, evidence_points: list) -> Optional[GeneratedResources]:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("DEEPSEEK_BASE_URL")
    model_name = os.environ.get("OPENAI_MODEL") or os.environ.get("DEEPSEEK_MODEL") or "deepseek-chat"
    
    if not api_key:
        return None

    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 结合知识图谱规划路径
    kg = KnowledgeGraphManager()
    mastered = state.learner_profile.get("mastered_points", [])
    target_algo = state.target_algorithm
    
    current_focus = kg.recommend_next_node(target_algo, mastered)
    full_path = kg.recommend_learning_path(target_algo, mastered)
    
    current_focus_name = kg.nodes_meta.get(current_focus, {}).get("name", current_focus)
    path_names = [kg.nodes_meta.get(n, {}).get("name", n) for n in full_path]
    
    system_prompt = "你是一个经验丰富的机器学习讲师。你的任务是根据学习者的当前状态和知识图谱路径，生成JSON格式的个性化实训资源。"
    
    user_prompt = f"""
    最终学习目标: {target_algo}
    未掌握的学习路径: {' -> '.join(path_names)}
    
    【核心指令】: 每次只专注生成当前最紧缺的那一个前置知识点的讲义，学完一个再解锁下一个！
    当前急需掌握的核心焦点: {current_focus_name}
    
    学习者级别: {level}
    参考资料: {', '.join(evidence_titles)}
    
    请围绕【{current_focus_name}】生成教学内容，严格按照以下JSON结构返回：
    {{
        "title": "{current_focus_name} 实训讲义 (通向 {target_algo} 的第1步)",
        "learner_level": "{level}",
        "theory_note": "...",
        "dataset_instruction": "...",
        "practice_guide": [
            {{ "step_name": "...", "python_code": "...", "explanation": "..." }}
        ],
        "graded_quiz": [
            {{ "level": "基础", "question": "...", "answer": "...", "explanation": "..." }},
            {{ "level": "标准", "question": "...", "answer": "...", "explanation": "..." }},
            {{ "level": "进阶", "question": "...", "answer": "...", "explanation": "..." }}
        ],
        "learning_path": {json.dumps(path_names, ensure_ascii=False)},
        "citations": {json.dumps(evidence_titles, ensure_ascii=False)}
    }}
    注意：只返回合法的JSON，不要有Markdown格式标记（如```json），确保能被JSON.loads解析。
    讲义内容必须紧紧围绕【{current_focus_name}】展开，不要超纲讲后面的节点。
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            timeout=15.0
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        data = json.loads(content)
        return GeneratedResources(**data)
    except Exception as e:
        print(f"LLM generation failed: {e}")
        return None

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

    resources = GeneratedResources(
        title=f"{state.target_algorithm}个性化实训资源",
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
        citations=evidence_titles,
    )
    return resources

def _beginner_theory(algorithm: str) -> str:
    return f"{algorithm}可以先理解成一个概率打分器：模型把多个特征加权求和，再通过 Sigmoid 函数压缩到 0 到 1 之间。数学基础薄弱时，不必先深究推导，重点理解它如何把样本分成两类，以及为什么要用训练集学习参数、用测试集检查泛化效果。"

def _intermediate_theory(algorithm: str) -> str:
    return f"{algorithm}的核心是用线性函数得到打分 $z = w^Tx + b$，再用 Sigmoid 函数 $\\sigma(z)=1/(1+e^{{-z}})$ 转成概率。训练过程会最小化分类损失，使正类样本概率更接近 1，负类样本概率更接近 0。"

def _advanced_theory(algorithm: str) -> str:
    return f"{algorithm}可视为广义线性模型在二分类任务中的典型形式。除了掌握 $\\sigma(w^Tx+b)$ 与交叉熵损失，还应关注正则化、类别不平衡、阈值移动和概率校准对工程效果的影响。"
