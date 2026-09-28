from unittest.mock import Mock
from repopilot.workflow import IssueWorkflow
from repopilot.github_flow import GitHubIssue
from repopilot.generator import GeneratedPatch

def test_issue_workflow_prepares_changes_without_applying(tmp_path):
    github = Mock()
    github.get_issue.return_value = GitHubIssue(12, "Fix login", "Handle invalid token")
    planner = Mock()
    planner.create.return_value = {"steps": ["inspect"], "risks": []}
    generator = Mock()
    generator.generate.return_value = [GeneratedPatch("app.py", "print('fixed')\n")]

    result = IssueWorkflow(github, planner, generator).prepare(
        "owner", "repo", 12, str(tmp_path), Mock()
    )

    assert result.issue.number == 12
    assert result.changes[0].path == "app.py"
    assert not (tmp_path / "app.py").exists()
