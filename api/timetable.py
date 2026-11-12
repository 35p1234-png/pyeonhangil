
import json
import os
from urllib.parse import urlencode, unquote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE_URL = "http://apis.data.go.kr/1613000/SubwayInfo"

def send_json(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)

def query_tago(operation, params):
    key = os.environ.get("TAGO_API_KEY")
    if not key:
        raise RuntimeError("Vercel 환경변수 TAGO_API_KEY를 찾을 수 없습니다. 저장 후 재배포했는지 확인해 주세요.")
    # URL-encoded key와 일반 인증키 모두 처리할 수 있도록 한 번 디코딩 후 urlencode합니다.
    params = dict(params)
    params["serviceKey"] = unquote(key)
    params["_type"] = "json"
    url = f"{BASE_URL}/{operation}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "Pyeonhan-gil/1.0", "Accept": "application/json"})
    try:
        with urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"TAGO HTTP 오류 {exc.code}: {detail}")
    except URLError as exc:
        raise RuntimeError(f"TAGO 서버에 연결하지 못했습니다: {exc.reason}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError("TAGO 응답을 JSON으로 해석하지 못했습니다. 인증키 형식 또는 응답 형식을 확인해 주세요.")
    response_data = data.get("response", data)
    header = response_data.get("header", {}) if isinstance(response_data, dict) else {}
    result_code = str(header.get("resultCode", "00"))
    if result_code != "00":
        raise RuntimeError(f"TAGO 오류 {result_code}: {header.get('resultMsg', '알 수 없는 오류')}")
    body = response_data.get("body", {}) if isinstance(response_data, dict) else {}
    items = body.get("items", {}) if isinstance(body, dict) else {}
    item_list = items.get("item", []) if isinstance(items, dict) else []
    if item_list is None:
        item_list = []
    elif isinstance(item_list, dict):
        item_list = [item_list]
    return item_list, body.get("totalCount", len(item_list))


from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        send_json(self, 200, {"ok": True})

    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            station_id = (query.get("stationId") or [""])[0].strip()
            day = (query.get("dailyTypeCode") or ["01"])[0]
            direction = (query.get("upDownTypeCode") or ["D"])[0]
            if not station_id:
                send_json(self, 400, {"ok": False, "message": "stationId가 필요합니다."})
                return
            if day not in ("01", "02", "03") or direction not in ("U", "D"):
                send_json(self, 400, {"ok": False, "message": "요일 또는 상하행 코드가 올바르지 않습니다."})
                return
            params = {"subwayStationId": station_id, "dailyTypeCode": day,
                      "upDownTypeCode": direction, "numOfRows": 300, "pageNo": 1}
            items, total = query_tago("GetSubwaySttnAcctoSchdulList", params)
            send_json(self, 200, {"ok": True, "items": items, "totalCount": total})
        except Exception as exc:
            send_json(self, 502, {"ok": False, "message": str(exc), "items": []})
