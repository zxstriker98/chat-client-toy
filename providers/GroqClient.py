import os
from openai import OpenAI, AsyncOpenAI
from providers.openai_compat_base import OpenAICompatClient, AsyncOpenAICompatClient


class GroqClient(OpenAICompatClient):
    """Synchronous Groq client (OpenAI-compatible API)."""

    def _create_client(self) -> OpenAI:
        return OpenAI(
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            api_key=os.getenv("GROQ_API_KEY", ""),
        )


class AsyncGroqClient(AsyncOpenAICompatClient):
    """Asynchronous Groq client (OpenAI-compatible API)."""

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            api_key=os.getenv("GROQ_API_KEY", ""),
        )
