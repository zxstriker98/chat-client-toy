import os
from openai import AsyncOpenAI
from providers.openai_compat_base import AsyncOpenAICompatClient


class AsyncGrokClient(AsyncOpenAICompatClient):
    """Asynchronous Grok client (OpenAI-compatible API)."""

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            base_url=os.getenv("GROK_BASE_URL", "https://api.x.ai/v1"),
            api_key=os.getenv("XAI_API_KEY", ""),
        )
