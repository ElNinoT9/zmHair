"""轻量 /health：不 import FastAPI，避免 30s 超时。"""
import json

from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(
            {
                "status": "ok",
                "service": "zmhair",
                "storage": {
                    "engine": "postgresql",
                    "persistent": True,
                    "note": "Neon 持久化；员工数据需本机脚本导入一次",
                },
            },
            ensure_ascii=False,
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode())
