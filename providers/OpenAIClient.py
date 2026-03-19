from openai import AsyncOpenAI
from providers.openai_compat_base import AsyncOpenAICompatClient


class AsyncOpenAIClient(AsyncOpenAICompatClient):
    """Asynchronous OpenAI client."""

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI()
