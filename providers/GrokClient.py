import os
from openai import OpenAI, AsyncOpenAI
from providers.openai_compat_base import OpenAICompatClient, AsyncOpenAICompatClient


class GrokClient(OpenAICompatClient):
    """Synchronous Grok client (OpenAI-compatible API)."""

    def _create_client(self) -> OpenAI:
        return OpenAI(
            base_url=os.getenv("GROK_BASE_URL", "https://api.x.ai/v1"),
            api_key=os.getenv("XAI_API_KEY", ""),
        )


class AsyncGrokClient(AsyncOpenAICompatClient):
    """Asynchronous Grok client (OpenAI-compatible API)."""

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            base_url=os.getenv("GROK_BASE_URL", "https://api.x.ai/v1"),
            api_key=os.getenv("XAI_API_KEY", ""),
        )
