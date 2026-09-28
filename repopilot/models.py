from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileInfo:
    path: str
    language: str
    lines: int
    size: int


@dataclass
class RepoMap:
    root: str
    files: list[FileInfo] = field(default_factory=list)

    @property
    def total_lines(self) -> int:
        return sum(item.lines for item in self.files)

    @property
    def total_size(self) -> int:
        return sum(item.size for item in self.files)
