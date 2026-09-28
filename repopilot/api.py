from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from pathlib import Path
import json
import os

from .agent import RepoAgent
from .config import ModelConfig
from .dependencies import build_dependency_graph
from .diff import unified_diff
from .generator import PatchGenerator
from .github_flow import GitHubClient
from .gitflow import run_git
from .models import RepoMap
from .patcher import apply_change, build_change
from .planner import Planner
from .providers_factory import create_provider
from .scanner import scan_repository
from .service import analyze_repository
from .verify import run_tests


def _root(value):
    root = Path(value or ".").expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    return root


def _map(root):
    return scan_repository(root)


def _provider():
    return create_provider(ModelConfig.from_env())


def _json_body(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length else b"{}"
    return json.loads(raw.decode("utf-8"))


def _issue_payload(issue):
    return {"number": issue.number, "title": issue.title, "body": issue.body}


class Handler(BaseHTTPRequestHandler):
    server_version = "RepoPilot/0.2"

    def _send(self, payload, status=200, content_type="application/json"):
        if content_type == "application/json":
            data = json.dumps(payload).encode("utf-8")
        else:
            data = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _error(self, exc, status=400):
        return self._send({"error": str(exc), "type": type(exc).__name__}, status)

    def do_OPTIONS(self):
        self._send({}, 204)

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/":
                dashboard = Path(__file__).resolve().parent.parent / "dashboard" / "index.html"
                return self._send(dashboard.read_text(encoding="utf-8"), 200, "text/html")
            if path == "/health":
                return self._send({"status": "ok", "provider": ModelConfig.from_env().provider})
            if path == "/analyze":
                return self._send(analyze_repository(_root(".")))
            if path == "/git/status":
                return self._send({"output": run_git(_root("."), "status", "--short", approved=True).output})
            return self._send({"error": "not found"}, 404)
        except Exception as exc:
            return self._error(exc, 500)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = _json_body(self)
            root = _root(body.get("root", "."))
            if path == "/api/analyze":
                return self._send(analyze_repository(root))
            if path == "/api/ask":
                question = str(body.get("question", "")).strip()
                if not question: raise ValueError("question is required")
                answer = RepoAgent(_provider()).ask(question, _map(root))
                return self._send({"answer": answer})
            if path == "/api/plan":
                goal = str(body.get("goal", "")).strip()
                if not goal: raise ValueError("goal is required")
                plan = Planner(_provider()).create(goal, str(root), _map(root))
                return self._send({"goal": plan.goal, "steps": plan.steps, "risks": plan.risks})
            if path == "/api/generate":
                goal = str(body.get("goal", "")).strip()
                if not goal: raise ValueError("goal is required")
                patches = PatchGenerator(_provider()).generate(goal, str(root), _map(root))
                result = []
                for patch in patches:
                    change = build_change(root, patch.path, patch.content)
                    result.append({"path": patch.path, "diff": change.diff(), "before": change.before, "after": change.after})
                return self._send({"patches": result, "approval_required": True})
            if path == "/api/apply":
                if body.get("approved") is not True: raise PermissionError("Explicit approval is required.")
                applied = []
                for item in body.get("changes", []):
                    change = build_change(root, item["path"], item["after"])
                    apply_change(root, change, approved=True)
                    applied.append(item["path"])
                return self._send({"applied": applied})
            if path == "/api/verify":
                if body.get("approved") is not True: raise PermissionError("Explicit approval is required.")
                result = run_tests(root, approved=True, timeout=int(body.get("timeout", 120)))
                return self._send({"command": result.command, "returncode": result.returncode, "output": result.output})
            if path == "/api/git":
                if body.get("approved") is not True: raise PermissionError("Explicit approval is required.")
                args = body.get("args") or ["status", "--short"]
                if not isinstance(args, list) or not all(isinstance(x, str) for x in args): raise ValueError("args must be a string list")
                return self._send({"output": run_git(root, *args, approved=True).output})
            if path == "/api/issue":
                if body.get("approved") is not True: raise PermissionError("Explicit approval is required for GitHub network access.")
                token = os.getenv("GITHUB_TOKEN")
                if not token: raise ValueError("GITHUB_TOKEN is not configured")
                issue = GitHubClient(token).get_issue(body["owner"], body["repo"], int(body["number"]))
                return self._send(_issue_payload(issue))
            if path == "/api/pr":
                if body.get("approved") is not True: raise PermissionError("Explicit approval is required for PR creation.")
                token = os.getenv("GITHUB_TOKEN")
                if not token: raise ValueError("GITHUB_TOKEN is not configured")
                client = GitHubClient(token)
                result = client.create_pull_request(body["owner"], body["repo"], body["title"], body.get("body", ""), body["head"], body.get("base", "main"))
                return self._send({"url": result.get("html_url"), "number": result.get("number"), "title": result.get("title")})
            return self._send({"error": "not found"}, 404)
        except PermissionError as exc:
            return self._error(exc, 403)
        except KeyError as exc:
            return self._error(ValueError(f"missing field: {exc.args[0]}"), 400)
        except Exception as exc:
            return self._error(exc, 400)


def serve(host="127.0.0.1", port=8765):
    ThreadingHTTPServer((host, port), Handler).serve_forever()
