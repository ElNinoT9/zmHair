#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "========================================"
echo "  理发预约系统 - 前端生产打包"
echo "========================================"

cd "$ROOT/front"
if [ ! -d node_modules ]; then
  npm install
fi
npm run build

echo
echo "打包完成: front/dist/"
echo "请将 dist 目录部署到 Web 服务器（IIS / Nginx）"
echo "详见 deploy/部署说明.md"
