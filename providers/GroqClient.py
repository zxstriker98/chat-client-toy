import os
from openai import AsyncOpenAI
from providers.openai_compat_base import AsyncOpenAICompatClient


class AsyncGroqClient(AsyncOpenAICompatClient):
    """Asynchronous Groq client (OpenAI-compatible API)."""

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            api_key=os.getenv("GROQ_API_KEY", ""),
        )
