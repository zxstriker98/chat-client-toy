from providers import AsyncBaseLLMClient, AsyncOllamaClient, AsyncOpenAIClient, AsyncAnthropicClient
from typing import Any, Final

MODEL_PROVIDERS: Final[dict[str, type[AsyncBaseLLMClient]]] = {
    "ollama": AsyncOllamaClient,
    "openai": AsyncOpenAIClient,
    "claude": AsyncAnthropicClient,
}

MODEL_PREFIXES: Final[dict[str, str]] = {
    "llama": "ollama",
    "gpt": "openai",
    "opus": "claude",
    "sonnet": "claude"
}


class ProviderFactory:
    @staticmethod
    def from_model(model_name: str, **kwargs: Any) -> AsyncBaseLLMClient:
        for prefix, provider in MODEL_PREFIXES.items():
            if model_name.lower().startswith(prefix.lower()):
                client_class = MODEL_PROVIDERS[provider]
                return client_class(model=model_name, **kwargs)
        return AsyncOllamaClient(model=model_name, **kwargs)
