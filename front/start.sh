#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "========================================"
echo "  企业内部理发预约系统 - 前端启动"
echo "========================================"
echo

if ! command -v npm >/dev/null 2>&1; then
  echo "错误: 未找到 npm，请先安装 Node.js"
  exit 1
fi

if [ ! -d "node_modules" ]; then
  echo "[1/2] 安装依赖..."
  npm install
else
  echo "[1/2] 依赖已存在"
fi

echo "[2/2] 启动开发服务..."
echo "  前端: http://127.0.0.1:8080"
echo "  请确保后端已启动: back 目录执行 ./start.sh"
echo

exec npm run serve
