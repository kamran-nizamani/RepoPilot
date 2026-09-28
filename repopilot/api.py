from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import json
from .service import analyze_repository

class Handler(BaseHTTPRequestHandler):
    def _send(self, payload, status=200):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:8765")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self._send({}, 204)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            return self._send({"status": "ok"})
        if path == "/analyze":
            try:
                return self._send(analyze_repository("."))
            except Exception as exc:
                return self._send({"error": str(exc)}, 500)
        return self._send({"error": "not found"}, 404)

def serve(host="127.0.0.1", port=8765):
    ThreadingHTTPServer((host, port), Handler).serve_forever()
