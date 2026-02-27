from openai import OpenAI, AsyncOpenAI
from providers.openai_compat_base import OpenAICompatClient, AsyncOpenAICompatClient

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"


class OllamaClient(OpenAICompatClient):
    """Synchronous Ollama providers (OpenAI-compatible API)."""

    def _create_client(self) -> OpenAI:
        return OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)


class AsyncOllamaClient(AsyncOpenAICompatClient):
    """Asynchronous Ollama providers (OpenAI-compatible API)."""

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)
