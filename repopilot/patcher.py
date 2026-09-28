from pathlib import Path
from .diff import ProposedChange

class PatchError(Exception):
    pass

def build_change(root: str | Path, path: str, new_content: str) -> ProposedChange:
    base = Path(root).resolve()
    target = (base / path).resolve()
    if base not in target.parents and target != base:
        raise PatchError("Path escapes repository root.")
    before = target.read_text(encoding="utf-8") if target.exists() else ""
    return ProposedChange(path=path, before=before, after=new_content)

def apply_change(root: str | Path, change: ProposedChange, approved: bool = False) -> None:
    if not approved:
        raise PermissionError("Explicit approval is required before applying a patch.")
    base = Path(root).resolve()
    target = (base / change.path).resolve()
    if base not in target.parents and target != base:
        raise PatchError("Path escapes repository root.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(change.after, encoding="utf-8")
