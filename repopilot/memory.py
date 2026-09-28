from dataclasses import dataclass, field
import json
from pathlib import Path

@dataclass
class ProjectMemory:
    facts: dict[str, str] = field(default_factory=dict)

    def remember(self, key: str, value: str) -> None:
        self.facts[key] = value

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.facts, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path):
        target = Path(path)
        if not target.exists():
            return cls()
        return cls(json.loads(target.read_text(encoding="utf-8")))
