from dataclasses import dataclass
import subprocess
from pathlib import Path

@dataclass
class VerificationResult:
    command: list[str]
    returncode: int
    output: str

def run_tests(root: str | Path) -> VerificationResult:
    process = subprocess.run(
        ["python", "-m", "pytest", "-q"],
        cwd=Path(root),
        text=True,
        capture_output=True,
        timeout=120,
    )
    return VerificationResult(
        command=["python", "-m", "pytest", "-q"],
        returncode=process.returncode,
        output=(process.stdout + process.stderr).strip(),
    )
