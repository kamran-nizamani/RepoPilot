from dataclasses import dataclass
import subprocess
from pathlib import Path
from .safety import SafetyPolicy, require_approval

@dataclass
class VerificationResult:
    command: list[str]
    returncode: int
    output: str

def run_tests(root: str | Path, approved: bool = False, timeout: int = 120) -> VerificationResult:
    """Run pytest only when shell execution has been explicitly approved."""
    require_approval("shell", approved)
    policy = SafetyPolicy(allow_shell=approved)
    if not policy.check("shell"):
        raise PermissionError("Shell execution is disabled by the safety policy.")
    command = ["python", "-m", "pytest", "-q"]
    try:
        process = subprocess.run(command, cwd=Path(root), text=True, capture_output=True, timeout=timeout)
        return VerificationResult(command, process.returncode, (process.stdout + process.stderr).strip())
    except subprocess.TimeoutExpired as exc:
        output = ((exc.stdout or "") + (exc.stderr or "")).strip()
        return VerificationResult(command, 124, output + "\nTest run timed out.")
