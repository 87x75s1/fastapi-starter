@echo off
chcp 65001 >nul
cd /d %~dp0
echo ========================================
echo   FastAPI 小程序后台 - 启动中...
echo   接口文档: http://127.0.0.1:8000/docs
echo   按 Ctrl+C 停止服务
echo ========================================
.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000