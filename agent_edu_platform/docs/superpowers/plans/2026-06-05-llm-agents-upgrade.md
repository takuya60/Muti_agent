# LLM Agents Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将画像诊断、路径规划、审核纠偏、反馈规划 4 个 Agent 升级为 LLM 驱动，并支持路径规划时动态向图谱写入新节点。

**Architecture:** 提取公共的 `llm_service.py` 处理所有的 OpenAI API 调用并强制 JSON 输出。各个 Agent 分别构造对应的 prompt，调用服务后进行数据解析，失败时 Fallback 到原有纯代码规则逻辑。对于动态节点，通过扩展 `graph_builder.py` 支持写入图谱文件，并在 `path_planner.py` 中应用。

**Tech Stack:** Python, LangGraph, OpenAI SDK, Pydantic, JSON

---

### Task 1: Create Shared LLM Service

**Files:**
- Create: `e:\挑战杯\agent_edu_platform\agents\llm_service.py`

- [ ] **Step 1: Write implementation**

```python
import json
import logging
from openai import OpenAI
from backend.config import settings

logger = logging.getLogger(__name__)

def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    timeout: float = 30.0,
    temperature: float = 0.3,
) -> dict:
    """
    调用 DeepSeek LLM 并返回解析后的 JSON dict。
    失败时抛出异常，由调用方决定如何 fallback。
    """
    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 未配置")
        
    client = OpenAI(api_key=api_key, base_url=settings.DEEPSEEK_BASE_URL)
    
    response = client.chat.completions.create(
        model=settings.DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        timeout=timeout,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content.strip()
    return json.loads(content)
```

- [ ] **Step 2: Commit**

```bash
git add agents/llm_service.py
git commit -m "feat: add shared llm service for structured JSON output"
```

### Task 2: Extend Knowledge Graph for Dynamic Nodes

**Files:**
- Modify: `e:\挑战杯\agent_edu_platform\knowledge_graph\graph_builder.py`

- [ ] **Step 1: Write implementation for `add_dynamic_node` and `save`**

Update `KnowledgeGraphManager` to support adding new nodes and persisting them.

```python
    def add_dynamic_node(self, node_data: dict) -> bool:
        """动态向图谱中添加新节点，成功返回 True"""
        node_id = node_data.get("id")
        if not node_id or node_id in self.graph:
            return False
            
        # 添加节点
        self.graph.add_node(
            node_id, 
            id=node_id,
            name=node_data.get("name", node_id),
            category=node_data.get("category", "动态扩展")
        )
        self.nodes_meta[node_id] = node_data
        
        # 添加前置依赖关系
        for prereq in node_data.get("prerequisites", []):
            if prereq in self.graph:
                self.graph.add_edge(prereq, node_id, relation_type="prerequisite")
                
        # 持久化到 JSON
        self.save()
        return True

    def save(self):
        """保存当前图谱状态到 JSON 文件"""
        import json
        data = {
            "nodes": [data for _, data in self.graph.nodes(data=True)],
            "edges": [{"from": u, "to": v, "type": d.get("relation_type", "related")} for u, v, d in self.graph.edges(data=True)]
        }
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
```

- [ ] **Step 2: Commit**

```bash
git add knowledge_graph/graph_builder.py
git commit -m "feat: support dynamic node injection in knowledge graph"
```

### Task 3: Upgrade Diagnosis Agent

**Files:**
- Modify: `e:\挑战杯\agent_edu_platform\agents\diagnosis_agent.py`

- [ ] **Step 1: Write implementation**

Replace the existing logic to use `llm_service`. Rename old logic to `_fallback_diagnosis`.

```python
import json
import logging
from typing import Any
from schemas.agent_state_schema import DiagnosisResult, WorkflowState
from agents.llm_service import call_llm_json

logger = logging.getLogger(__name__)

# ... (Keep existing dictionaries _SCORE_THRESHOLDS, _LEVEL_LABELS, _INITIAL_WEAK_POINTS) ...

def _fallback_diagnosis(state: WorkflowState) -> DiagnosisResult:
    # ... (Move the old run_diagnosis_agent logic here, returning DiagnosisResult) ...
    pass

def _llm_diagnosis(state: WorkflowState) -> DiagnosisResult:
    profile_json = json.dumps(state.learner_profile, ensure_ascii=False)
    system_prompt = '''你是一个专业的机器学习教育学情诊断专家。
请根据用户的画像数据，深度分析用户的学习状态。
你需要输出一个严格合法的 JSON 对象，格式要求如下：
{
  "weak_points": ["薄弱点1", "薄弱点2"],
  "strengths": ["优势1", "优势2"],
  "recommended_level": "beginner|beginner_plus|intermediate|advanced",
  "learning_objectives": ["目标1", "目标2", "目标3"],
  "explanation_strategy": "..."
}'''
    
    data = call_llm_json(system_prompt, f"用户画像数据：\n{profile_json}")
    
    level = data.get("recommended_level", "beginner_plus")
    if level not in ["beginner", "beginner_plus", "intermediate", "advanced"]:
        level = "beginner_plus"
        
    return DiagnosisResult(
        weak_points=data.get("weak_points", []),
        strengths=data.get("strengths", []),
        recommended_level=level,
        learning_objectives=data.get("learning_objectives", ["明确当前学习起点和下一步路径"]),
        explanation_strategy=data.get("explanation_strategy", "用案例和图解降低理解门槛"),
    )

def run_diagnosis_agent(state: WorkflowState) -> WorkflowState:
    try:
        diagnosis = _llm_diagnosis(state)
        agent_status = "llm_completed"
        logger.info(f"LLM 画像诊断成功，推荐难度：{diagnosis.recommended_level}")
    except Exception as e:
        logger.warning(f"LLM 画像诊断失败 ({type(e).__name__}: {e})，降级为规则诊断")
        diagnosis = _fallback_diagnosis(state)
        agent_status = "fallback_completed"
        
    state.diagnosis = diagnosis
    state.agent_events.append({
        "agent": "画像诊断 Agent",
        "status": "completed",
        "engine": "llm" if agent_status == "llm_completed" else "fallback",
        "summary": f"[{'LLM 诊断' if agent_status == 'llm_completed' else '规则降级'}] 识别出 {len(diagnosis.weak_points)} 个薄弱点，策略：{diagnosis.explanation_strategy}",
    })
    return state
```

- [ ] **Step 2: Commit**

```bash
git add agents/diagnosis_agent.py
git commit -m "feat: upgrade diagnosis agent to LLM driven"
```

### Task 4: Upgrade Path Planner Agent

**Files:**
- Modify: `e:\挑战杯\agent_edu_platform\agents\path_planner.py`

- [ ] **Step 1: Write implementation**

Rename old logic to `_fallback_resolve_direction` and `_fallback_infer_mastered_nodes`.
Add `_get_path_decision` utilizing LLM and supporting dynamic node insertion.

```python
import json
import logging
from typing import Any
from agents.llm_service import call_llm_json

logger = logging.getLogger(__name__)

# ... (Keep existing dictionaries, rename old functions to _fallback_*) ...

def _llm_path_decision(learner: dict[str, Any], target_algorithm: str, profile_level: str, kg: Any) -> tuple[str, list[str], str, list[str]]:
    context = {
        "learner_profile": learner,
        "target_algorithm": target_algorithm,
        "profile_level": profile_level,
        "available_branches": {k: v["title"] for k, v in BRANCH_META.items()},
        "foundation_nodes": FOUNDATION_NODES,
        "branch_nodes": BRANCH_NODES
    }
    
    system_prompt = '''你是一个智能的学习路径规划师。
根据用户画像和目标，挑选最合适的分支，推断已掌握节点，并可按需补充新的学习节点。
JSON 格式要求如下：
{
  "target_direction": "classification", // 必须是 available_branches 的键之一
  "mastered_nodes": ["python_basics"], // 必须从 foundation_nodes 或 branch_nodes 挑选
  "recommended_reason": "你已具备 Python 基础，推荐进入分类...",
  "new_nodes": [ // 最多3个。如果在已有图谱里找不到合适的进阶/细化节点，可以在这里提议
    {"id": "xgboost", "name": "XGBoost", "category": "集成学习", "branch": "model_explanation", "prerequisites": ["gradient_boosting"]}
  ]
}'''
    
    data = call_llm_json(system_prompt, f"规划数据：\n{json.dumps(context, ensure_ascii=False)}")
    
    direction = data.get("target_direction")
    if direction not in BRANCH_META:
        direction = "classification"
        
    mastered = data.get("mastered_nodes", [])
    valid_mastered = [n for n in mastered if n in FOUNDATION_NODES or any(n in nodes for nodes in BRANCH_NODES.values())]
    reason = data.get("recommended_reason", "系统基于画像推荐了此路径。")
    
    # 动态节点处理
    added_nodes = []
    for node_data in data.get("new_nodes", [])[:3]: # 最多3个
        branch = node_data.get("branch")
        if branch in BRANCH_NODES and kg.add_dynamic_node(node_data):
            BRANCH_NODES[branch].append(node_data["id"])
            added_nodes.append(node_data["id"])
            
    return direction, valid_mastered, reason, added_nodes

def _get_path_decision(learner: dict[str, Any], target_algorithm: str, kg: Any) -> tuple[str, list[str], str, list[str]]:
    profile_level = learner.get("current_level", "beginner_plus")
    try:
        return _llm_path_decision(learner, target_algorithm, profile_level, kg)
    except Exception as e:
        logger.warning(f"LLM 路径规划失败 ({type(e).__name__}: {e})")
        return _fallback_resolve_direction(learner, target_algorithm), _fallback_infer_mastered_nodes(learner, profile_level), "", []

def build_learning_plan(learner: dict[str, Any], target_algorithm: str, kg: Any) -> LearningPlan:
    direction, mastered_list, llm_reason, new_nodes = _get_path_decision(learner, target_algorithm, kg)
    mastered = set(mastered_list)
    # ... existing path generation code ...
```

- [ ] **Step 2: Commit**

```bash
git add agents/path_planner.py
git commit -m "feat: upgrade path planner to LLM and support dynamic nodes"
```

### Task 5: Upgrade Reviewer Agent

**Files:**
- Modify: `e:\挑战杯\agent_edu_platform\agents\reviewer_agent.py`

- [ ] **Step 1: Write implementation**

Combine hard-rule checks with LLM content evaluation.

```python
import json
import logging
from schemas.agent_state_schema import WorkflowState
from agents.llm_service import call_llm_json

logger = logging.getLogger(__name__)

# ... (Keep existing _REQUIRED_RESOURCE_KEYS, _FORBIDDEN_PATTERNS) ...

def _hard_rule_review(state: WorkflowState) -> list[str]:
    # ... (Extract the existing checks into this function, return a list of issue strings) ...
    return []

def _llm_review(resources: dict, evidence_titles: list[str]) -> tuple[bool, list[str], str]:
    resources_summary = {
        "theory_note_preview": resources.get("theory_note", "")[:500],
        "quiz_count": len(resources.get("graded_quiz", [])),
        "code_preview": str(resources.get("practice_guide", []))[:500],
        "citations": resources.get("citations", [])
    }
    
    system_prompt = '''你是一个严格的教育内容审核专家。
请检查提供的教学资源是否结构完整、逻辑连贯、难度匹配，并且引用的知识库证据真实有效。
JSON 格式要求如下：
{
  "passed": true|false,
  "issues": ["问题1"], // 如果 passed 为 true，这里应该为空数组
  "summary": "审核通过..."
}'''

    data = call_llm_json(system_prompt, f"知识库证据：{evidence_titles}\n生成资源：\n{json.dumps(resources_summary, ensure_ascii=False)}")
    return data.get("passed", False), data.get("issues", []), data.get("summary", "LLM审核完成")

def run_reviewer_agent(state: WorkflowState) -> WorkflowState:
    resources = state.generated_resources or {}
    evidence_titles = [item.title for item in state.retrieved_knowledge]
    
    # 1. 代码层硬规则检查
    hard_issues = _hard_rule_review(state)
    
    # 2. LLM 检查
    llm_issues = []
    llm_summary = "LLM 审核完成"
    agent_status = "fallback"
    
    try:
        llm_passed, llm_issues, llm_summary = _llm_review(resources, evidence_titles)
        agent_status = "llm"
    except Exception as e:
        logger.warning(f"LLM 审核失败 ({e})")
        
    all_issues = hard_issues + llm_issues
    
    if all_issues:
        state.review_passed = False
        state.reviewer_feedback = "；".join(all_issues)
        status = "failed"
        summary = state.reviewer_feedback
    else:
        state.review_passed = True
        state.reviewer_feedback = llm_summary if agent_status == "llm" else "规则审核通过"
        status = "completed"
        summary = state.reviewer_feedback

    state.agent_events.append({
        "agent": "审核纠偏 Agent",
        "status": status,
        "engine": agent_status,
        "summary": f"[{'LLM 审核' if agent_status == 'llm' else '规则降级'}] {summary}",
    })
    _sync_agent_trace(resources, "审核纠偏 Agent", status, summary)
    return state
```

- [ ] **Step 2: Commit**

```bash
git add agents/reviewer_agent.py
git commit -m "feat: upgrade reviewer agent to use dual checks (LLM + Hard Rules)"
```

### Task 6: Upgrade Feedback Planner Agent

**Files:**
- Modify: `e:\挑战杯\agent_edu_platform\agents\feedback_agent.py`

- [ ] **Step 1: Write implementation**

Rename old logic to `_fallback_feedback`.

```python
import json
import logging
from schemas.agent_state_schema import WorkflowState
from agents.llm_service import call_llm_json

logger = logging.getLogger(__name__)

def _fallback_feedback(quiz_accuracy: float | None, learner_feedback: str) -> tuple[str, str]:
    # ... (Return action, resource_type using existing logic) ...
    pass

def _llm_feedback(quiz_accuracy: float | None, learner_feedback: str) -> tuple[str, str]:
    system_prompt = '''你是一个学习反馈规划师。
根据学生的测验准确率和反馈，决定下一步的教学动作和资源类型。
JSON 格式要求如下：
{
  "next_action": "生成降维解释...",
  "resource_type": "standard_practice|remedial_explanation|advanced_challenge|reinforcement"
}'''
    data = call_llm_json(system_prompt, f"准确率：{quiz_accuracy}\n用户反馈：{learner_feedback}")
    
    rt = data.get("resource_type", "standard_practice")
    if rt not in ["standard_practice", "remedial_explanation", "advanced_challenge", "reinforcement"]:
        rt = "standard_practice"
        
    return data.get("next_action", "保持当前路径"), rt

def run_feedback_agent(state: WorkflowState, quiz_accuracy: float | None = None, learner_feedback: str = "") -> WorkflowState:
    try:
        action, resource_type = _llm_feedback(quiz_accuracy, learner_feedback)
        engine = "llm"
    except Exception as e:
        logger.warning(f"LLM 反馈规划失败 ({e})")
        action, resource_type = _fallback_feedback(quiz_accuracy, learner_feedback)
        engine = "fallback"

    state.feedback_decision = {
        "quiz_accuracy": quiz_accuracy,
        "learner_feedback": learner_feedback,
        "next_action": action,
        "resource_type": resource_type,
    }
    state.agent_events.append({
        "agent": "反馈规划 Agent",
        "status": "completed",
        "engine": engine,
        "summary": f"[{'LLM 规划' if engine == 'llm' else '规则降级'}] {action}",
    })
    _sync_agent_trace(state.generated_resources or {}, action)
    return state
```

- [ ] **Step 2: Commit**

```bash
git add agents/feedback_agent.py
git commit -m "feat: upgrade feedback agent to LLM driven"
```

---
