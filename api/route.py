
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # TAGO SubwayInfo provides station lookup, timetable, and exit-area facilities.
        # It does not provide an origin-destination route graph or route-planning operation.
        body = {
            "ok": False,
            "message": "현재 연결된 TAGO 지하철정보 API는 출발역-도착역 전체 경로, 소요 시간, 거리, 환승 횟수를 계산하지 않습니다. 역 검색·시간표·출구 주변 시설만 조회할 수 있습니다."
        }
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(501)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)
