# 部署说明

## 本地运行

```bash
pip install -r requirements.txt
python scripts/run_demo.py
streamlit run frontend/app.py
uvicorn backend.main:app --reload
```

## 配置说明

复制 `.env.example` 为 `.env`，填入模型 API Key。当前骨架支持离线规则版本，便于先跑通系统闭环。
