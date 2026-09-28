from dataclasses import dataclass
import ast
from pathlib import Path

from .models import RepoMap

@dataclass(frozen=True)
class ASTSymbol:
    name: str
    kind: str
    path: str
    line: int
    end_line: int | None

def index_python_ast(root: str | Path, repo_map: RepoMap) -> list[ASTSymbol]:
    base = Path(root).resolve()
    result = []
    for item in repo_map.files:
        if item.language != "Python":
            continue
        try:
            source = (base / item.path).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=item.path)
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                result.append(ASTSymbol(
                    node.name,
                    "class" if isinstance(node, ast.ClassDef) else "function",
                    item.path,
                    node.lineno,
                    getattr(node, "end_lineno", None),
                ))
    return result
