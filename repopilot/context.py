from pathlib import Path
from .models import RepoMap
from .search import search_text

def build_context(root: str | Path, repo_map: RepoMap, query: str, limit: int = 8) -> str:
    matches = search_text(root, repo_map, query, limit=limit)
    if not matches:
        return "No direct source matches found."
    base = Path(root).resolve()
    chunks = []
    for path, line, _ in matches:
        lines = (base / path).read_text(encoding="utf-8").splitlines()
        start, end = max(0, line - 3), min(len(lines), line + 2)
        excerpt = "\n".join(f"{i + 1}: {lines[i]}" for i in range(start, end))
        chunks.append(f"### {path}\n{excerpt}")
    return "\n\n".join(chunks)
