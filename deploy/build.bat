@echo off
chcp 65001 >nul
cd /d "%~dp0\..\front"

echo ========================================
echo   理发预约系统 - 前端生产打包
echo ========================================

if not exist "node_modules\" (
    call npm install
)
call npm run build

echo.
echo 打包完成: front\dist\
echo 请将 dist 目录设为 IIS 站点根目录
echo 详见 deploy\部署说明.md
pause
