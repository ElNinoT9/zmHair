"""轻量 /health：不加载 FastAPI，避免 504。"""
import json

from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(
            {
                "status": "ok",
                "service": "zmhair",
                "note": "数据库状态见登录后业务；完整 storage 字段见 FastAPI 就绪后 /api 路由",
            }
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body.encode())
