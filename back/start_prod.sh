#!/usr/bin/env bash
# 生产环境启动后端（Linux）

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ ! -d "venv" ]; then
  echo "错误: 请先运行 ./start.sh 初始化虚拟环境"
  exit 1
fi

PY="$ROOT/venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "错误: 找不到 venv Python"
  exit 1
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
  echo "提示: 已复制 .env.example，请修改 SECRET_KEY"
fi

export RELOAD=false
export HOST=127.0.0.1
export PORT=8001

PORT=8001
if command -v lsof >/dev/null 2>&1; then
  OLD_PIDS=$(lsof -t -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)
  if [ -n "$OLD_PIDS" ]; then
    kill $OLD_PIDS 2>/dev/null || true
    sleep 1
  fi
fi

echo "========================================"
echo "  理发预约系统 - 后端 API（生产）"
echo "  127.0.0.1:8001"
echo "========================================"

if "$PY" -c "import gunicorn" 2>/dev/null; then
  exec "$PY" -m gunicorn main:app \
    -w 2 \
    -k uvicorn.workers.UvicornWorker \
    -b 127.0.0.1:8001 \
    --access-logfile - \
    --error-logfile -
else
  echo "未安装 gunicorn，使用 uvicorn 单进程启动"
  exec "$PY" main.py
fi
