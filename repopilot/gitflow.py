from dataclasses import dataclass
import re
import subprocess
from pathlib import Path
from .safety import require_approval

@dataclass(frozen=True)
class GitResult:
    command: tuple[str, ...]
    returncode: int
    output: str

class GitError(RuntimeError):
    pass

def run_git(root: str | Path, *args: str, approved: bool = False) -> GitResult:
    require_approval("shell", approved)
    result = subprocess.run(["git", *args], cwd=Path(root), text=True, capture_output=True, timeout=120)
    output = (result.stdout + result.stderr).strip()
    if result.returncode:
        raise GitError(f"git {' '.join(args)} failed: {output}")
    return GitResult(tuple(["git", *args]), result.returncode, output)

def create_branch(root: str | Path, name: str, start_point: str = "HEAD", approved: bool = False) -> GitResult:
    if not name or name.startswith("-") or not re.fullmatch(r"[A-Za-z0-9._/-]+", name):
        raise ValueError("Invalid branch name.")
    return run_git(root, "switch", "-c", name, start_point, approved=approved)

def commit_changes(root: str | Path, message: str, approved: bool = False) -> GitResult:
    if not message.strip():
        raise ValueError("Commit message is required.")
    run_git(root, "add", "-A", approved=approved)
    return run_git(root, "commit", "-m", message, approved=approved)

def push_branch(root: str | Path, remote: str = "origin", branch: str | None = None, approved: bool = False) -> GitResult:
    require_approval("network", approved)
    branch = branch or run_git(root, "branch", "--show-current", approved=approved).output
    return run_git(root, "push", "-u", remote, branch, approved=approved)
