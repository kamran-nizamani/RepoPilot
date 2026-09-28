from dataclasses import dataclass
import subprocess
from pathlib import Path

@dataclass(frozen=True)
class GitResult:
    command: tuple[str, ...]
    returncode: int
    output: str

class GitError(RuntimeError):
    pass

def run_git(root: str | Path, *args: str) -> GitResult:
    result = subprocess.run(["git", *args], cwd=Path(root), text=True,
                            capture_output=True, timeout=120)
    output = (result.stdout + result.stderr).strip()
    if result.returncode:
        raise GitError(f"git {' '.join(args)} failed: {output}")
    return GitResult(tuple(["git", *args]), result.returncode, output)

def create_branch(root: str | Path, name: str, start_point: str = "HEAD") -> GitResult:
    if not name or name.startswith("-") or " " in name:
        raise ValueError("Invalid branch name.")
    return run_git(root, "switch", "-c", name, start_point)

def commit_changes(root: str | Path, message: str) -> GitResult:
    if not message.strip():
        raise ValueError("Commit message is required.")
    return run_git(root, "add", "-A") and run_git(root, "commit", "-m", message)

def push_branch(root: str | Path, remote: str = "origin", branch: str | None = None) -> GitResult:
    branch = branch or run_git(root, "branch", "--show-current").output
    return run_git(root, "push", "-u", remote, branch)
