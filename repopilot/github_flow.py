from dataclasses import dataclass
import json
from urllib.request import Request, urlopen

@dataclass(frozen=True)
class GitHubIssue:
    number: int
    title: str
    body: str

class GitHubClient:
    """Small stdlib GitHub API client. Network actions are explicit at the caller."""
    def __init__(self, token: str, api_url: str = "https://api.github.com"):
        self.token = token
        self.api_url = api_url.rstrip("/")

    def _request(self, method: str, path: str, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        request = Request(f"{self.api_url}{path}", data=data, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }, method=method)
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_issue(self, owner: str, repo: str, number: int) -> GitHubIssue:
        data = self._request("GET", f"/repos/{owner}/{repo}/issues/{number}")
        return GitHubIssue(number, data.get("title", ""), data.get("body") or "")

    def create_pull_request(self, owner: str, repo: str, title: str, body: str, head: str, base: str = "main"):
        return self._request("POST", f"/repos/{owner}/{repo}/pulls", {
            "title": title, "body": body, "head": head, "base": base,
        })
