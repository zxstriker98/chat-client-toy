from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field
from typing import Any
from tools.tools import ToolRegistry, registry
from client.models import Conversation, ConversationHistory


class BaseLLMClient(BaseModel, ABC):
    """Abstract base class for synchronous LLM clients.

    Provider-agnostic — subclasses implement all provider-specific logic
    (client creation, API calls, tool formatting, response parsing).
    """

    client: Any = None
    model: str = ""
    conversation_history: ConversationHistory = Field(
        default_factory=lambda: ConversationHistory(conversations=[])
    )
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

    def __init__(
        self, model: str, instructions: str, tool_registry: ToolRegistry = registry
    ) -> None:
        super().__init__(
            client=None,
            model=model,
            instructions=instructions,
            conversation_history=ConversationHistory(conversations=[]),
            tool_registry=tool_registry,
        )
        object.__setattr__(self, "client", self._create_client())

    def generate_response(self, query: str) -> str:
        self.conversation_history.append_user_query(query)

        while True:
            kwargs: dict[str, Any] = self._build_request_kwargs()
            response: Any = self._call_api(**kwargs)

            tool_calls = self._extract_tool_calls(response)

            if not tool_calls:
                return self._process_text_response(self._extract_text(response))

            for tool_call in tool_calls:
                self._execute_tool_call(tool_call)

        return ""

    def _process_text_response(self, output_text: str) -> str:
        print(output_text)
        self.conversation_history.append_assistant_response(output_text)
        return output_text


class AsyncBaseLLMClient(BaseModel, ABC):
    """Abstract base class for asynchronous LLM clients.

    Provider-agnostic — subclasses implement all provider-specific logic
    (client creation, API calls, tool formatting, response parsing).
    """

    client: Any = None
    model: str = ""
    conversation_history: ConversationHistory = Field(
        default_factory=lambda: ConversationHistory(conversations=[])
    )
    instructions: str = ""
    tool_registry: ToolRegistry = registry

    model_config = ConfigDict(arbitrary_types_allowed=True)

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

    def __init__(
        self, model: str, instructions: str, tool_registry: ToolRegistry = registry
    ) -> None:
        super().__init__(
            client=None,
            model=model,
            instructions=instructions,
            conversation_history=ConversationHistory(conversations=[]),
            tool_registry=tool_registry,
        )
        object.__setattr__(self, "client", self._create_client())

    async def generate_response(self, query: str) -> str:
        self.conversation_history.append_user_query(query)

        while True:
            kwargs: dict[str, Any] = self._build_request_kwargs()
            response: Any = await self._call_api(**kwargs)

            tool_calls = self._extract_tool_calls(response)

            if not tool_calls:
                return self._process_text_response(self._extract_text(response))

            for tool_call in tool_calls:
                self._execute_tool_call(tool_call)

        return ""

    def _process_text_response(self, output_text: str) -> str:
        print(output_text)
        self.conversation_history.append_assistant_response(output_text)
        return output_text
