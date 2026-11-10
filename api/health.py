
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        response = {
            "status": "success",
            "message": "편한길 API 서버 연결 성공!",
            "service": "Pyeonhan-gil"
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        self.wfile.write(
            json.dumps(response, ensure_ascii=False).encode("utf-8")
        )
