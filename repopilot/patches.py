from dataclasses import dataclass
import difflib


@dataclass
class PatchProposal:
    path: str
    original: str
    proposed: str

    def diff(self) -> str:
        return "".join(
            difflib.unified_diff(
                self.original.splitlines(keepends=True),
                self.proposed.splitlines(keepends=True),
                fromfile=f"a/{self.path}",
                tofile=f"b/{self.path}",
            )
        )

    def apply(self, approved: bool) -> None:
        if not approved:
            raise PermissionError("Patch rejected: approval is required before file writes.")
