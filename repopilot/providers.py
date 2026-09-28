from dataclasses import dataclass
from typing import Protocol
import json
from urllib.request import Request, urlopen

@dataclass
class ModelResponse:
    text: str
    provider: str

class ModelProvider(Protocol):
    name: str
    def complete(self, prompt: str) -> ModelResponse: ...

class MockProvider:
    name = "mock"
    def complete(self, prompt: str) -> ModelResponse:
        return ModelResponse("Mock provider response. Configure Ollama for local AI.", self.name)

class OllamaProvider:
    name = "ollama"
    def __init__(self, model="llama3.2", base_url="http://localhost:11434"):
        self.model, self.base_url = model, base_url.rstrip("/")

    def complete(self, prompt: str) -> ModelResponse:
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        request = Request(f"{self.base_url}/api/generate", data=payload,
                          headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        return ModelResponse(data.get("response", ""), self.name)
