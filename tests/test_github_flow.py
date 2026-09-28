from unittest.mock import patch
from repopilot.github_flow import GitHubClient

def test_github_issue_request_uses_auth():
    client = GitHubClient("secret")
    with patch.object(client, "_request", return_value={"number": 7, "title": "Fix bug", "body": "details"}):
        issue = client.get_issue("owner", "repo", 7)
    assert issue.number == 7
    assert issue.title == "Fix bug"

def test_create_pr_payload():
    client = GitHubClient("secret")
    with patch.object(client, "_request", return_value={"number": 8} ) as request:
        client.create_pull_request("owner", "repo", "Fix bug", "summary", "fix/bug")
    request.assert_called_once_with("POST", "/repos/owner/repo/pulls", {
        "title": "Fix bug", "body": "summary", "head": "fix/bug", "base": "main"
    })
