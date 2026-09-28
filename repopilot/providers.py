from dataclasses import dataclass
from typing import Protocol


@dataclass
class ModelResponse:
    text: str
    provider: str


class ModelProvider(Protocol):
    name: str

    def complete(self, prompt: str) -> ModelResponse:
        ...


class MockProvider:
    """Deterministic provider used by the CLI foundation and tests."""

    name = "mock"

    def complete(self, prompt: str) -> ModelResponse:
        return ModelResponse(
            text="RepoPilot provider is ready. Connect a model provider to generate AI responses.",
            provider=self.name,
        )
