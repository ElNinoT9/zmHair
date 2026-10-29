#!/usr/bin/env bash
# 企业内部理发预约系统 - Mac/Linux 一键启动后端

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "========================================"
echo "  企业内部理发预约系统 - 后端启动"
echo "========================================"
echo

pick_python() {
  for cmd in python3.11 python3.10 python3; do
    if command -v "$cmd" >/dev/null 2>&1; then
      local ver
      ver=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
      local major minor
      major=${ver%%.*}
      minor=${ver#*.}
      if [ "$major" -eq 3 ] && [ "$minor" -ge 14 ]; then
        continue
      fi
      echo "$cmd"
      return 0
    fi
  done
  return 1
}

venv_python() {
  for py in "$ROOT/venv/bin/python3.11" "$ROOT/venv/bin/python3.10" "$ROOT/venv/bin/python3" "$ROOT/venv/bin/python"; do
    if [ -x "$py" ]; then
      echo "$py"
      return 0
    fi
  done
  return 1
}

venv_ok() {
  local py ver major minor
  py=$(venv_python) || return 1
  ver=$("$py" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  major=${ver%%.*}
  minor=${ver#*.}
  if [ "$major" -eq 3 ] && [ "$minor" -ge 14 ]; then
    return 1
  fi
  "$py" -c "import uvicorn, fastapi" 2>/dev/null
}

if [ ! -d "venv" ] || ! venv_ok; then
  if [ -d "venv" ]; then
    echo "[1/3] 虚拟环境不兼容（需 Python 3.10/3.11），正在重建..."
    rm -rf venv
  else
    echo "[1/3] 创建虚拟环境..."
  fi
  PY=$(pick_python) || {
    echo "错误: 未找到 Python 3.10 或 3.11"
    echo "  例如: brew install python@3.11"
    exit 1
  }
  echo "  使用: $PY ($("$PY" --version))"
  "$PY" -m venv venv
else
  echo "[1/3] 虚拟环境已存在"
fi

PY=$(venv_python) || {
  echo "错误: 无法找到 venv 中的 Python"
  exit 1
}

echo "[2/3] 安装依赖..."
"$PY" -m pip install --upgrade pip -q
"$PY" -m pip install -r requirements.txt -q

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
fi

PORT=8001
if [ -f ".env" ]; then
  ENV_PORT=$(grep -E '^PORT=' .env | tail -1 | cut -d= -f2 | tr -d '\r')
  if [ -n "$ENV_PORT" ]; then
    PORT="$ENV_PORT"
  fi
fi

if command -v lsof >/dev/null 2>&1; then
  OLD_PIDS=$(lsof -t -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)
  if [ -n "$OLD_PIDS" ]; then
    echo "  端口 $PORT 已被占用，正在结束旧进程: $OLD_PIDS"
    kill $OLD_PIDS 2>/dev/null || true
    sleep 1
    STILL=$(lsof -t -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)
    if [ -n "$STILL" ]; then
      kill -9 $STILL 2>/dev/null || true
      sleep 1
    fi
  fi
fi

echo "[3/3] 启动服务（开发模式，端口 $PORT）..."
echo
echo "  API 文档: http://127.0.0.1:$PORT/docs"
echo "  健康检查: http://127.0.0.1:$PORT/health"
echo "  默认管理员: admin / admin123"
echo

export RELOAD=true
export PORT="$PORT"
exec "$PY" main.py
