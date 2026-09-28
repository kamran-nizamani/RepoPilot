from pathlib import Path

from .models import RepoMap
from .providers import ModelProvider


class RepoAgent:
    def __init__(self, provider: ModelProvider):
        self.provider = provider

    def ask(self, question: str, repo_map: RepoMap) -> str:
        files = "\n".join(
            f"- {item.path} ({item.language}, {item.lines} lines)"
            for item in repo_map.files[:80]
        )
        prompt = f"""You are RepoPilot, a repository-aware coding agent.

Repository files:
{files}

User request:
{question}

Return a concise engineering response. Do not claim to have changed files."""
        return self.provider.complete(prompt).text
