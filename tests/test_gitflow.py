from unittest.mock import patch
from repopilot.gitflow import run_git

def test_run_git_builds_safe_command(tmp_path):
    with patch("repopilot.gitflow.subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "main"
        run.return_value.stderr = ""
        result = run_git(tmp_path, "branch", "--show-current", approved=True)
    assert result.output == "main"
    run.assert_called_once()
