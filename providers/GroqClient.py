import os
from openai import OpenAI, AsyncOpenAI
from providers.openai_compat_base import OpenAICompatClient, AsyncOpenAICompatClient

GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class GroqClient(OpenAICompatClient):
    """Synchronous Groq client (OpenAI-compatible API)."""

    def _create_client(self) -> OpenAI:
        return OpenAI(base_url=GROQ_BASE_URL, api_key=GROQ_API_KEY)


class AsyncGroqClient(AsyncOpenAICompatClient):
    """Asynchronous Groq client (OpenAI-compatible API)."""

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=GROQ_API_KEY)
