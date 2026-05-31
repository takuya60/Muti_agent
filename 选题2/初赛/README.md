# 初赛 README

## 这是什么

基于 Intern-S1 的数学智能体，用于挑战杯赛题 XH-202627 **初赛**。

初赛目标很简单：**调用 Intern-S1 把所有数学题跑一遍，尽量答对，输出合法 JSON。**

## 核心流程

```text
题目 → Intern-S1 推理 → 提取答案 → (SymPy 校验) → (修正重试) → JSON 输出
```

不搞多 Agent，不搞复杂架构。把正确率和效率做到最好。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API
cp .env.example .env
# 编辑 .env，填入 INTERN_S1_API_KEY 和 INTERN_S1_BASE_URL

# 3. 批量处理
python solve.py --batch data/problems/ --output data/results/
```

## 目录结构

```text
初赛/
├── core/                     # API 调用、答案提取、配置
├── schemas/                  # JSON 输出格式定义
├── tools/                    # SymPy 校验 (可选)
├── prompts/                  # Prompt 模板
├── logging_system/           # JSONL 日志
├── data/
│   ├── problems/             # 赛题数据
│   ├── results/              # 输出结果
│   └── logs/                 # 运行日志
├── solve.py                  # 主入口
└── requirements.txt
```

## 文档

| 文档 | 内容 |
|---|---|
| [architecture.md](architecture.md) | 初赛架构设计 + 核心代码示例 |
| [task_checklist.md](task_checklist.md) | 开发任务清单 (4 个 Checkpoint) |
| [prompt_engineering.md](prompt_engineering.md) | Prompt 工程指南 |

## 初赛 vs 决赛

| | 初赛 | 决赛 |
|---|---|---|
| 架构 | 单智能体 | 多 Agent 协作 |
| 重点 | 正确率 + 效率 | 架构 + 交互 Demo |
| 代码量 | ~500 行 | ~3000+ 行 |
| 框架 | 不需要 | LangGraph |

初赛做好，决赛再扩展。
