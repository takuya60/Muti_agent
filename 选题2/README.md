# MathAgent 数学智能体 - 项目说明

基于 Intern-S1 的数学智能体设计与推理创新分析系统。本项目用于挑战杯赛题 XH-202627。

## 项目定位

围绕 Intern-S1 模型 API，构建一个能自动求解数学题、校验答案、解释推理过程、输出稳定 JSON 结果的多智能体系统。重点展示题型路由、工具增强推理、三级校验闭环、自我修正和启发式解释。

## 核心能力

- **18 领域题型路由**：代数、微积分、微分方程、复分析、拓扑、运筹等精准分发。
- **7 类 Agent 协同**：Router → Planner → Solver → Tool → Verifier → Explainer → Formatter。
- **数学工具链**：SymPy 符号计算 + NumPy/SciPy 数值验证 + OR-Tools 优化 + NetworkX 图论。
- **三级校验**：符号校验 + 数值校验 + 逻辑校验，多层互补保障正确率。
- **自我修正**：校验失败后提取错误原因，定向重推，最多 N 次。
- **稳定 JSON 输出**：Pydantic 强约束 + 格式自动修复。
- **全链路日志**：每题保存完整 JSONL 日志，支持复现与分析。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env

# 批量处理
python run_batch.py --input data/problems/competition_data/ --output data/results/

# 启动 Demo
python run_demo.py
```

## 项目结构

```text
math_agent/
├── agents/           #  智能体逻辑层 (Router/Planner/Solver/Verifier/Explainer/Formatter)
├── core/             #  核心基础设施 (API Client/Config/Retry)
├── tools/            #  数学工具链 (SymPy/NumPy/SciPy/OR-Tools/NetworkX)
├── schemas/          #  Pydantic 数据契约
├── prompts/          #  Prompt 模板库
├── logging_system/   #  JSONL 日志系统
├── evaluation/       #  评测系统
├── batch/            #  批量处理 + 断点续跑
├── demo/             #  Gradio/Streamlit Demo
├── data/             #  题目 + 结果 + 日志
├── tests/            #  测试
└── notebooks/        #  分析 Notebook
```

## 文档

- [详尽架构白皮书](docs/project_detailed_architecture.md)
- [技术路线与开发计划](docs/technical_roadmap.md)
- [与选题1 (AgentEdu) 对比分析](docs/comparison_with_topic1.md)

## 技术栈

| 分类 | 技术 |
|---|---|
| 核心模型 | Intern-S1 API |
| Agent 框架 | LangGraph + lagent |
| 符号计算 | SymPy |
| 数值计算 | NumPy / SciPy / mpmath |
| 优化工具 | OR-Tools / PuLP |
| 图论工具 | NetworkX |
| 数据契约 | Pydantic |
| Demo | Gradio / Streamlit |
