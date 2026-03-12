import asyncio
import sys
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from typing import Any, AsyncIterator
from tools.tools import ToolRegistry, registry
from providers.models import Conversation

# Default timeout (seconds) for a single LLM API call.
DEFAULT_API_TIMEOUT: int = 120

# Maximum number of consecutive tool-call rounds before we force a text reply.
MAX_TOOL_ROUNDS: int = 20

class BaseLLMClient(BaseModel, ABC):
    """Abstract base class for synchronous LLM clients.

    Provider-agnostic — subclasses implement all provider-specific logic
    (client creation, API calls, tool formatting, response parsing).
    """

    client: Any = None
    model: str = ""
    conversation_history: list[Conversation] = Field(default_factory=list)
    instructions: str = ""
    tool_registry: ToolRegistry = registry

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def _create_client(self) -> Any:
        """Create and return the provider-specific client instance."""
        ...

    @abstractmethod
    def _call_api(self, **kwargs: Any) -> Any:
        """Make a synchronous API call and return the raw provider response."""
        ...

    @abstractmethod
    def _build_request_kwargs(self) -> dict[str, Any]:
        """Build provider-specific request keyword arguments."""
        ...

    @abstractmethod
    def _extract_tool_calls(self, response: Any) -> list[Any]:
        """Extract tool call objects from the provider response. Return empty list if none."""
        ...

    @abstractmethod
    def _extract_text(self, response: Any) -> str:
        """Extract the text content from the provider response."""
        ...

    @abstractmethod
    def _execute_tool_call(self, tool_call: Any) -> None:
        """Execute a single tool call and record it in conversation history."""
        ...

    def _pre_tool_hook(self, response: Any) -> None:
        """Optional hook called before executing tool calls. Override to add provider-specific logic."""
        pass

    def __init__(
        self, model: str, instructions: str, tool_registry: ToolRegistry = registry
    ) -> None:
        super().__init__(
            client=None,
            model=model,
            instructions=instructions,
            conversation_history=[],
            tool_registry=tool_registry,
        )
        object.__setattr__(self, "client", self._create_client())

    def generate_response(self, query: str) -> str:
        self.conversation_history.append(Conversation(role="user", content=query))

        for round_num in range(MAX_TOOL_ROUNDS):
            kwargs: dict[str, Any] = self._build_request_kwargs()
            response: Any = self._call_api(**kwargs)

            tool_calls: list[Any] = self._extract_tool_calls(response)

            if not tool_calls:
                return self._process_text_response(self._extract_text(response))

            self._pre_tool_hook(response)

            for tool_call in tool_calls:
                self._execute_tool_call(tool_call)

        # If we exhausted the tool-call budget, return whatever text we have.
        print("[Warning: max tool-call rounds reached, returning partial response]")
        return self._process_text_response(self._extract_text(response))

    def _process_text_response(self, output_text: str) -> str:
        print(output_text)
        self.conversation_history.append(Conversation(role="assistant", content=output_text))
        return output_text


class AsyncBaseLLMClient(BaseModel, ABC):
    """Abstract base class for asynchronous LLM clients.

    Provider-agnostic — subclasses implement all provider-specific logic
    (client creation, API calls, tool formatting, response parsing).
    """

    client: Any = None
    model: str = ""
    conversation_history: list[Conversation] = Field(default_factory=list)
    instructions: str = ""
    tool_registry: ToolRegistry = registry
    _last_stream_response: Any | None = PrivateAttr(default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    async def _call_api_streaming(self, **kwargs: Any) -> AsyncIterator[str]:
        """
        Stream tokens from the provider. Yields text chunks as they arrive.

        Should yield text strings for content, and raise / return when tool calls are detected
        """

    @abstractmethod
    def _create_client(self) -> Any:
        """Create and return the provider-specific async client instance."""
        ...

    @abstractmethod
    async def _call_api(self, **kwargs: Any) -> Any:
        """Make an asynchronous API call and return the raw provider response."""
        ...

    @abstractmethod
    def _build_request_kwargs(self) -> dict[str, Any]:
        """Build provider-specific request keyword arguments."""
        ...

    @abstractmethod
    def _extract_tool_calls(self, response: Any) -> list[Any]:
        """Extract tool call objects from the provider response. Return empty list if none."""
        ...

    @abstractmethod
    def _extract_text(self, response: Any) -> str:
        """Extract the text content from the provider response."""
        ...

    @abstractmethod
    def _execute_tool_call(self, tool_call: Any) -> None:
        """Execute a single tool call and record it in conversation history."""
        ...

    def _pre_tool_hook(self, response: Any) -> None:
        """Optional hook called before executing tool calls. Override to add provider-specific logic."""
        pass

    def _pre_tool_hook_streaming(self) -> None:
        pass

    def __init__(
        self, model: str, instructions: str, tool_registry: ToolRegistry = registry
    ) -> None:
        super().__init__(
            client=None,
            model=model,
            instructions=instructions,
            conversation_history=[],
            tool_registry=tool_registry,
        )
        object.__setattr__(self, "client", self._create_client())

    async def generate_response(self, query: str) -> str:
        self.conversation_history.append(Conversation(role="user", content=query))

        response: Any = None
        for round_num in range(MAX_TOOL_ROUNDS):
            kwargs: dict[str, Any] = self._build_request_kwargs()
            try:
                response = await asyncio.wait_for(
                    self._call_api(**kwargs),
                    timeout=DEFAULT_API_TIMEOUT,
                )
            except asyncio.TimeoutError:
                msg = f"[Error: LLM API call timed out after {DEFAULT_API_TIMEOUT}s]"
                print(msg)
                self.conversation_history.append(Conversation(role="assistant", content=msg))
                return msg

            tool_calls: list[Any] = self._extract_tool_calls(response)

            if not tool_calls:
                return self._process_text_response(self._extract_text(response))

            self._pre_tool_hook(response)

            for tool_call in tool_calls:
                self._execute_tool_call(tool_call)

        # If we exhausted the tool-call budget, return whatever text we have.
        print("[Warning: max tool-call rounds reached, returning partial response]")
        final_text = self._extract_text(response) if response else ""
        return self._process_text_response(final_text)

    async def generate_response_streaming(self, query: str) -> str:
        """Like generate_response, but streams text tokens to stdout in real-time"""
        self.conversation_history.append(Conversation(role="user", content=query))

        full_text = ""
        for round_num in range(MAX_TOOL_ROUNDS):
            self._last_stream_response = None
            kwargs = self._build_request_kwargs()
            kwargs["stream"] = True

            collected_text: list[str] = []

            async def _consume_stream() -> None:
                async for chunk in self._call_api_streaming(**kwargs):
                    if isinstance(chunk, str):
                        print(chunk, end="", flush=True)
                        collected_text.append(chunk)

            try:
                await asyncio.wait_for(
                    _consume_stream(),
                    timeout=DEFAULT_API_TIMEOUT,
                )
            except asyncio.TimeoutError:
                # Print whatever we collected so far, then warn the user.
                partial = "".join(collected_text)
                print(f"\n[Error: streaming response timed out after {DEFAULT_API_TIMEOUT}s]", flush=True)
                if partial:
                    self.conversation_history.append(
                        Conversation(role="assistant", content=partial)
                    )
                return partial

            full_text = "".join(collected_text)

            tool_calls: list[Any] = []
            if hasattr(self, '_last_stream_response') and self._last_stream_response:
                tool_calls = self._extract_tool_calls(self._last_stream_response)

            if not tool_calls:
                print(flush=True)
                self.conversation_history.append(
                    Conversation(role="assistant", content=full_text)
                )
                return full_text

            self._pre_tool_hook_streaming()
            for tool_call in tool_calls:
                self._execute_tool_call(tool_call)

        # If we exhausted the tool-call budget, return whatever we have.
        print("\n[Warning: max tool-call rounds reached, returning partial response]", flush=True)
        self.conversation_history.append(
            Conversation(role="assistant", content=full_text)
        )
        return full_text
                
    def _process_text_response(self, output_text: str) -> str:
        print(output_text)
        self.conversation_history.append(Conversation(role="assistant", content=output_text))
        return output_text
