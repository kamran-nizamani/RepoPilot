from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from .service import analyze_repository

class Handler(BaseHTTPRequestHandler):
    def _send(self, payload, status=200):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self._send({"status": "ok"})
        if self.path == "/analyze":
            try:
                return self._send(analyze_repository("."))
            except Exception as exc:
                return self._send({"error": str(exc)}, 500)
        return self._send({"error": "not found"}, 404)

def serve(host="127.0.0.1", port=8765):
    ThreadingHTTPServer((host, port), Handler).serve_forever()
