from dataclasses import dataclass
from pathlib import Path
import re

from .models import RepoMap

@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    path: str
    line: int
    message: str

RULES = [
    ("hardcoded-secret", "high", re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{8,}['\"]"),
     "Possible hardcoded secret."),
    ("dangerous-eval", "high", re.compile(r"\beval\s*\("), "Use of eval() can execute untrusted code."),
    ("shell-true", "medium", re.compile(r"subprocess\.[A-Za-z_]+\([^\n]*shell\s*=\s*True"), "subprocess call enables shell execution."),
]

def scan_security(root: str | Path, repo_map: RepoMap) -> list[Finding]:
    base = Path(root).resolve()
    findings = []
    for item in repo_map.files:
        if item.language not in {"Python", "JavaScript", "TypeScript"}:
            continue
        try:
            lines = (base / item.path).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(lines, 1):
            for rule, severity, pattern, message in RULES:
                if pattern.search(line):
                    findings.append(Finding(rule, severity, item.path, number, message))
    return findings
