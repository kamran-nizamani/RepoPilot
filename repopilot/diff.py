from dataclasses import dataclass
from difflib import unified_diff

@dataclass
class ProposedChange:
    path: str
    before: str
    after: str
    def diff(self) -> str:
        return ''.join(unified_diff(self.before.splitlines(True), self.after.splitlines(True), fromfile=f'a/{self.path}', tofile=f'b/{self.path}'))
