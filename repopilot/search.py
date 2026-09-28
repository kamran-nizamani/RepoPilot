from pathlib import Path
from .models import RepoMap

def search_text(root: str | Path, repo_map: RepoMap, query: str, limit: int = 20):
    base = Path(root).resolve()
    results = []
    for item in repo_map.files:
        try:
            lines = (base / item.path).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(lines, 1):
            if query.lower() in line.lower():
                results.append((item.path, number, line.strip()))
                if len(results) >= limit:
                    return results
    return results
