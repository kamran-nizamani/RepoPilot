from pathlib import Path
from .scanner import scan_repository
from .security import scan_security
from .dependencies import build_dependency_graph
from .ast_index import index_python_ast

def analyze_repository(root: str = ".") -> dict:
    repo = scan_repository(Path(root))
    return {
        "files": len(repo.files),
        "languages": sorted({f.language for f in repo.files}),
        "symbols": len(index_python_ast(root, repo)),
        "dependencies": len(build_dependency_graph(root, repo)),
        "security_findings": len(scan_security(root, repo)),
    }
