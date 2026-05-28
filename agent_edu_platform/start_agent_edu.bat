@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo AgentEdu 一键启动
echo ========================================
echo.

if not exist "frontend-vue\package.json" (
  echo [ERROR] 请把本脚本放在 agent_edu_platform 目录下运行。
  pause
  exit /b 1
)

if not exist ".env" (
  echo [WARN] 未发现 .env 文件。如果需要 LLM，请确认已配置 DEEPSEEK_API_KEY。
  echo.
)

echo [1/2] 启动 FastAPI 后端: http://localhost:8001
start "AgentEdu Backend" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001"

echo [2/2] 启动 Vue 前端: http://localhost:5173
start "AgentEdu Frontend" cmd /k "cd /d "%~dp0frontend-vue" && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo 已打开两个终端窗口：
echo - AgentEdu Backend  后端服务
echo - AgentEdu Frontend 前端服务
echo.
echo 浏览器访问: http://localhost:5173
echo 如果页面无法连接，请等待后端模型/服务加载完成后刷新。
echo.
pause
