"""
Vercel Serverless 入口：将 HTTP 请求转给 FastAPI 应用。
本地开发仍使用 back/main.py + uvicorn。
"""
import sys
from pathlib import Path

BACK_DIR = Path(__file__).resolve().parent.parent / "back"
if str(BACK_DIR) not in sys.path:
    sys.path.insert(0, str(BACK_DIR))

from main import app  # noqa: E402  Vercel ASGI
