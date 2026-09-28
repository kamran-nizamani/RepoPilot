from dataclasses import dataclass
from pathlib import Path
import re
from .models import RepoMap

@dataclass
class Symbol:
    name: str
    kind: str
    path: str
    line: int

PATTERNS = [
    ("class", re.compile(r"^\s*class\s+([A-Za-z_]\w*)")),
    ("function", re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)")),
]

def index_symbols(root: str | Path, repo_map: RepoMap) -> list[Symbol]:
    base = Path(root).resolve()
    symbols = []
    for item in repo_map.files:
        if item.language != "Python":
            continue
        try:
            lines = (base / item.path).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(lines, 1):
            for kind, pattern in PATTERNS:
                match = pattern.match(line)
                if match:
                    symbols.append(Symbol(match.group(1), kind, item.path, number))
    return symbols
