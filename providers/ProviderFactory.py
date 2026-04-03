from providers import AsyncBaseLLMClient, AsyncOllamaClient, AsyncOpenAIClient, AsyncAnthropicClient, AsyncGrokClient, AsyncGroqClient
from typing import Final
from tools.tools import ToolRegistry, registry

MODEL_PROVIDERS: Final[dict[str, type[AsyncBaseLLMClient]]] = {
    "ollama": AsyncOllamaClient,
    "openai": AsyncOpenAIClient,
    "claude": AsyncAnthropicClient,
    "grok": AsyncGrokClient,
    "groq": AsyncGroqClient,
}

MODEL_PREFIXES: Final[list[tuple[str, str]]] = [
    ("gpt", "openai"),
    ("o1", "openai"),
    ("claude", "claude"),
    ("grok", "grok"),
    ("llama", "groq"),
    ("mistral", "groq"),
    ("qwen", "groq"),
    ("openai/gpt-oss-120b", "groq")
]


class ProviderFactory:
    @staticmethod
    def from_model(
        model_name: str,
        instructions: str = "",
        tool_registry: ToolRegistry = registry,
    ) -> AsyncBaseLLMClient:
        """Resolve the provider from model name prefix and return an initialized client.
        
        Falls back to AsyncOllamaClient if no prefix matches.
        """
        for prefix, provider in MODEL_PREFIXES:
            if model_name.lower().startswith(prefix.lower()):
                client_class: type[AsyncBaseLLMClient] = MODEL_PROVIDERS[provider]
                return client_class(model=model_name, instructions=instructions, tool_registry=tool_registry)
        return AsyncOllamaClient(model=model_name, instructions=instructions, tool_registry=tool_registry)
