from pathlib import Path

from .models import FileInfo, RepoMap

IGNORED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", "dist", "build", ".next", ".idea", ".vscode"
}

EXTENSIONS = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".java": "Java",
    ".cpp": "C++", ".c": "C", ".h": "C/C++", ".hpp": "C++",
    ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".cs": "C#", ".json": "JSON", ".md": "Markdown",
    ".yml": "YAML", ".yaml": "YAML", ".toml": "TOML",
}


def scan_repository(root: str | Path) -> RepoMap:
    base = Path(root).resolve()
    if not base.is_dir():
        raise ValueError(f"Not a directory: {root}")

    result = RepoMap(root=str(base))
    for path in sorted(base.rglob("*")):
        if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
            continue
        language = EXTENSIONS.get(path.suffix.lower())
        if not language:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        result.files.append(
            FileInfo(
                path=path.relative_to(base).as_posix(),
                language=language,
                lines=len(text.splitlines()),
                size=path.stat().st_size,
            )
        )
    return result
