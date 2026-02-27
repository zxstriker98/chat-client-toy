from openai import OpenAI, AsyncOpenAI
from providers.openai_compat_base import OpenAICompatClient, AsyncOpenAICompatClient


class OpenAIClient(OpenAICompatClient):
    """Synchronous OpenAI providers."""

    def _create_client(self) -> OpenAI:
        return OpenAI()


class AsyncOpenAIClient(AsyncOpenAICompatClient):
    """Asynchronous OpenAI providers."""

    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI()
