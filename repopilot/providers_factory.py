from .config import ModelConfig
from .providers import MockProvider, OllamaProvider, ModelProvider

def create_provider(config: ModelConfig) -> ModelProvider:
    if config.provider == "ollama":
        return OllamaProvider(config.model, config.base_url)
    if config.provider == "mock":
        return MockProvider()
    raise ValueError(f"Unsupported provider: {config.provider}")
