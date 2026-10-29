@echo off
chcp 65001 >nul
title 理发预约系统 - 后端服务（生产）

cd /d "%~dp0"

if not exist "venv\" (
    echo 错误: 未找到虚拟环境，请先运行 start.bat 或 start.sh 完成初始化
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist ".env" (
    if exist ".env.example" copy .env.example .env
    echo 提示: 已复制 .env.example，请修改 SECRET_KEY 后重启
    echo.
)

set RELOAD=false
set HOST=127.0.0.1
set PORT=8001

echo ========================================
echo   理发预约系统 - 后端 API（生产）
echo   监听: 127.0.0.1:8001
echo   仅本机访问，由 IIS/Nginx 反向代理 /api
echo ========================================
echo.

python main.py
