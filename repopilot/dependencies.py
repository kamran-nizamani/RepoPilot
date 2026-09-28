from dataclasses import dataclass
import re
from pathlib import Path

from .models import RepoMap

@dataclass(frozen=True)
class Dependency:
    source: str
    target: str
    kind: str

_IMPORT = re.compile(r"^\s*(?:from\s+([\w.]+)|import\s+([\w.]+))")

def build_dependency_graph(root: str | Path, repo_map: RepoMap) -> list[Dependency]:
    base = Path(root).resolve()
    known = {Path(f.path).with_suffix("").as_posix().replace("/", ".") for f in repo_map.files if f.language == "Python"}
    result = []
    for item in repo_map.files:
        if item.language != "Python":
            continue
        source = Path(item.path).with_suffix("").as_posix().replace("/", ".")
        try:
            lines = (base / item.path).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line in lines:
            match = _IMPORT.match(line)
            target = (match.group(1) or match.group(2)) if match else None
            if target and any(target == k or target.startswith(k + ".") for k in known):
                result.append(Dependency(source, target, "import"))
    return result
