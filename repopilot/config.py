from dataclasses import dataclass
import os

@dataclass(frozen=True)
class ModelConfig:
    provider: str = "mock"
    model: str = "llama3.2"
    base_url: str = "http://localhost:11434"

    @classmethod
    def from_env(cls):
        return cls(
            provider=os.getenv("REPOPILOT_PROVIDER", "mock"),
            model=os.getenv("REPOPILOT_MODEL", "llama3.2"),
            base_url=os.getenv("REPOPILOT_BASE_URL", "http://localhost:11434"),
        )
