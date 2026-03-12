import os
from openai import OpenAI, AsyncOpenAI
from providers.openai_compat_base import OpenAICompatClient, AsyncOpenAICompatClient


class OllamaClient(OpenAICompatClient):
    """Synchronous Ollama client (OpenAI-compatible API)."""

    def _create_client(self) -> OpenAI:
        return OpenAI(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
        )


class AsyncOllamaClient(AsyncOpenAICompatClient):
    """Asynchronous Ollama client (OpenAI-compatible API)."""

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
        )
