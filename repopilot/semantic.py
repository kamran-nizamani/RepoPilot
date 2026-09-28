import math
import re
from collections import Counter
from pathlib import Path

from .models import RepoMap

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]+")

def _tokens(text: str) -> Counter:
    return Counter(t.lower() for t in _TOKEN.findall(text))

def rank_context(root: str | Path, repo_map: RepoMap, query: str, limit: int = 8):
    query_tokens = _tokens(query)
    if not query_tokens:
        return []
    base = Path(root).resolve()
    scored = []
    for item in repo_map.files:
        try:
            text = (base / item.path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        tokens = _tokens(text)
        dot = sum(query_tokens[t] * tokens[t] for t in query_tokens)
        qn = math.sqrt(sum(v*v for v in query_tokens.values()))
        dn = math.sqrt(sum(v*v for v in tokens.values()))
        score = dot / (qn * dn) if qn and dn else 0.0
        if score > 0:
            scored.append((score, item.path))
    return sorted(scored, reverse=True)[:limit]
