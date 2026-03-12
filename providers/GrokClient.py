import os
from openai import OpenAI, AsyncOpenAI
from providers.openai_compat_base import OpenAICompatClient, AsyncOpenAICompatClient

GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
GROK_API_KEY = os.getenv("XAI_API_KEY", "")


class GrokClient(OpenAICompatClient):
    """Synchronous Grok client (OpenAI-compatible API)."""

    def _create_client(self) -> OpenAI:
        return OpenAI(base_url=GROK_BASE_URL, api_key=GROK_API_KEY)


class AsyncGrokClient(AsyncOpenAICompatClient):
    """Asynchronous Grok client (OpenAI-compatible API)."""

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(base_url=GROK_BASE_URL, api_key=GROK_API_KEY)
