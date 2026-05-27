import json
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from agents.workflow import run_workflow
from frontend.components.agent_flow_view import render_agent_flow
from schemas.learner_schema import LearnerProfile
PROFILE_DIR = PROJECT_ROOT / "data" / "learner_profiles"


st.set_page_config(page_title="AgentEdu 多智能体实训平台", layout="wide")
st.title("领域知识个性化生成与多智能体协同决策系统")
st.caption("比赛 Demo：机器学习入门实训场景，展示画像诊断、RAG 检索、资源生成、审核纠偏与反馈决策闭环。")

profile_files = {path.stem: path for path in sorted(PROFILE_DIR.glob("*.json"))}
profile_name = st.sidebar.selectbox("选择学习者画像", list(profile_files))
quiz_accuracy = st.sidebar.slider("模拟答题正确率", 0.0, 1.0, 0.75, 0.05)
learner_feedback = st.sidebar.selectbox("学习者反馈", ["", "太难", "太简单", "想看案例"])

@st.dialog("三类画像对比")
def show_profile_comparison():
    data = []
    for name, path in profile_files.items():
        prof = json.loads(path.read_text(encoding="utf-8"))
        data.append({
            "画像类型": name,
            "背景": prof.get("background", ""),
            "目标": prof.get("goal", ""),
            "目标算法": prof.get("target_algorithm", ""),
            "偏好风格": prof.get("preferred_style", ""),
            "每周时长(h)": prof.get("available_time_per_week", 0)
        })
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True)

if st.sidebar.button("📊 查看三类画像对比"):
    show_profile_comparison()

profile_data = json.loads(profile_files[profile_name].read_text(encoding="utf-8"))
profile = LearnerProfile.model_validate(profile_data)

if st.sidebar.button("启动多 Agent 生成", type="primary"):
    with st.spinner("多智能体协同生成中..."):
        state = run_workflow(profile, quiz_accuracy=quiz_accuracy, learner_feedback=learner_feedback)
        st.session_state["state"] = state.model_dump()

state = st.session_state.get("state")

left, middle, right = st.columns([1, 1.2, 1.4])

with left:
    st.subheader("学习者画像")
    st.json(profile.model_dump(), expanded=True)
    
    if state and state.get("retrieved_knowledge"):
        st.subheader("RAG 检索证据")
        for ev in state["retrieved_knowledge"]:
            with st.expander(f"📄 {ev['title']} (Score: {ev.get('score', 0):.2f})"):
                st.markdown(ev["content"])
                st.caption(f"提取知识点：{', '.join(ev['knowledge_points'])}")

with middle:
    st.subheader("多 Agent 协同过程")
    if state:
        st.graphviz_chart(render_agent_flow(state["agent_events"]))
        for event in state["agent_events"]:
            status = event.get('status', 'completed')
            msg = f"**{event['agent']}**：{event['summary']}"
            if status == "error" or status == "failed":
                st.error(msg)
            elif status == "retry":
                st.warning(msg)
            else:
                st.success(msg)
        
        if state.get("reviewer_feedback"):
            st.subheader("审核纠偏意见")
            if state.get("review_passed"):
                st.success(state["reviewer_feedback"], icon="✅")
            else:
                st.warning(state["reviewer_feedback"], icon="⚠️")
    else:
        st.info("点击左侧按钮后展示 Agent 调度过程。")

with right:
    st.subheader("个性化资源")
    if state and state.get("generated_resources"):
        resources = state["generated_resources"]
        st.markdown(f"### {resources['title']}")
        st.info(f"适配难度：{resources.get('learner_level', '未知')}")
        
        st.markdown("#### 学习路径时间线")
        for i, step in enumerate(resources.get("learning_path", [])):
            st.markdown(f"**Step {i+1}:** {step}")
            
        st.markdown("---")
        st.markdown(resources["theory_note"])
        st.markdown("#### 实操指南")
        for step in resources["practice_guide"]:
            st.markdown(f"**{step['step_name']}**")
            st.code(step["python_code"], language="python")
            st.caption(step["explanation"])
            
        st.markdown("#### 分阶测试题")
        for quiz in resources["graded_quiz"]:
            st.markdown(f"- **{quiz['level']}**：{quiz['question']}")
            with st.expander("查看答案"):
                st.markdown(f"**答案**：{quiz['answer']}")
                st.markdown(f"**解析**：{quiz['explanation']}")
                
        st.markdown("#### 引用来源")
        st.write(resources["citations"])
    else:
        st.info("生成结果会在这里展示。")

if state:
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    evaluation = state["evaluation"]
    c1.metric("幻觉率估算", f"{evaluation['hallucination_rate']:.0%}")
    c2.metric("难度适配", f"{evaluation['difficulty_match']:.0%}")
    c3.metric("知识覆盖", f"{evaluation['knowledge_coverage']:.0%}")
    c4.metric("结构完整", f"{evaluation['structure_completeness']:.0%}")
    st.subheader("反馈决策")
    st.json(state["feedback_decision"])
