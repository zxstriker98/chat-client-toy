from providers import AsyncBaseLLMClient, AsyncOllamaClient, AsyncOpenAIClient, AsyncAnthropicClient
from typing import Any, Final

MODEL_PROVIDERS: Final[dict[str, type[AsyncBaseLLMClient]]] = {
    "ollama": AsyncOllamaClient,
    "openai": AsyncOpenAIClient,
    "claude": AsyncAnthropicClient,
}

MODEL_PREFIXES: Final[list[tuple[str, str]]] = [
    ("gpt", "openai"),
    ("o1", "openai"),
    ("claude", "claude"),
    ("llama", "ollama"),
    ("mistral", "ollama"),
    ("qwen", "ollama"),
]


class ProviderFactory:
    @staticmethod
    def from_model(model_name: str, **kwargs: Any) -> AsyncBaseLLMClient:
        for prefix, provider in MODEL_PREFIXES:
            if model_name.lower().startswith(prefix.lower()):
                client_class: type[AsyncBaseLLMClient] = MODEL_PROVIDERS[provider]
                return client_class(model=model_name, **kwargs)
        return AsyncOllamaClient(model=model_name, **kwargs)
