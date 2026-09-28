from dataclasses import dataclass
import re
from .context import build_context
from .models import RepoMap
from .providers import ModelProvider

@dataclass
class GeneratedPatch:
    path: str
    content: str

def parse_generated_patches(text: str) -> list[GeneratedPatch]:
    pattern = re.compile(r"FILE:\s*(.+)\n```(?:\w+)?\n(.*?)```", re.DOTALL)
    return [GeneratedPatch(m.group(1).strip(), m.group(2)) for m in pattern.finditer(text)]

class PatchGenerator:
    def __init__(self, provider: ModelProvider):
        self.provider = provider

    def generate(self, goal: str, root: str, repo_map: RepoMap) -> list[GeneratedPatch]:
        context = build_context(root, repo_map, goal)
        prompt = f"""Generate minimal code changes for this task:
{goal}

Relevant code:
{context}

Output only:
FILE: relative/path.py
```python
complete file content
```
Do not use absolute paths."""
        return parse_generated_patches(self.provider.complete(prompt).text)
