"""
Vercel Serverless 入口。
"""
import sys
from pathlib import Path

BACK_DIR = Path(__file__).resolve().parent.parent / "back"
if str(BACK_DIR) not in sys.path:
    sys.path.insert(0, str(BACK_DIR))

from main import app  # noqa: E402
