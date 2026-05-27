# AgentEdu 多智能体个性化实训平台

本项目用于挑战杯赛题 XH-202630「领域知识个性化生成与多智能体协同决策系统研究」。当前垂直场景选择为机器学习入门实训，重点展示多 Agent 协同、RAG 知识溯源、个性化资源生成、审核纠偏和反馈决策闭环。

## 当前骨架能力

- 三类学习者画像：基础薄弱型、普通基础型、进阶提升型。
- 五类 Agent：学情诊断、知识检索、资源生成、审核纠偏、反馈决策。
- 三类学习资源：定制讲义、实操指南、分阶测试题。
- 规则版评测指标：幻觉率估算、难度适配、知识覆盖、结构完整。
- Streamlit Demo 与 FastAPI 接口骨架。

## 快速启动

```bash
pip install -r requirements.txt
python scripts/run_demo.py
streamlit run frontend/app.py
uvicorn backend.main:app --reload
```

## 项目结构

```text
frontend/      Streamlit 演示界面
backend/       FastAPI 接口层
agents/        多智能体工作流与节点
rag_engine/    知识库检索模块
schemas/       Pydantic 数据协议
data/          知识库、画像、知识图谱和样例
evaluation/    指标计算与质量评测
tests/         自动化测试
scripts/       一键运行和数据导出脚本
docs/          比赛文档与部署说明
```

## 后续开发重点

1. 把 `agents/generator_agent.py` 从规则模板升级为 DeepSeek / Qwen 的结构化输出。
2. 把 `rag_engine/retriever.py` 从关键词检索升级为 Chroma / FAISS 向量检索。
3. 扩充知识库切片和测试样例，支撑幻觉率、适配率、覆盖率评测。
4. 优化 Streamlit 页面，增加学习路径图、难度匹配曲线和审核前后对比。
