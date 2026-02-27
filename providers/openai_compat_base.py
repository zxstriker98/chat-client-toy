"""Base classes for clients using the OpenAI-compatible SDK.

Any provider that speaks the OpenAI API (OpenAI, Ollama, Groq, Together AI, etc.)
can extend these classes and only override _create_client().
"""
from abc import ABC

import openai
from openai.types.responses import Response, FunctionToolParam, ResponseFunctionToolCall
from typing import Any
from providers.base import BaseLLMClient, AsyncBaseLLMClient
from providers.errors.ProviderError import AuthenticationError, RateLimitExceededError, ModelNotFoundError, ConnectionError, ProviderApiError
from providers.models import Conversation, OpenAiToolSchema


class OpenAICompatClient(BaseLLMClient, ABC):
    """Sync base for any provider using the OpenAI-compatible API."""

    def _call_api(self, **kwargs: Any) -> Response:
        try:
            return self.client.responses.create(**kwargs)
        except openai.AuthenticationError as e:
            raise AuthenticationError("Invalid API key", provider="openai", original_error=e)
        except openai.RateLimitError as e:
            raise RateLimitExceededError("Rate limit exceeded", provider="openai", original_error=e)
        except openai.NotFoundError as e:
            raise ModelNotFoundError(f"Model not found: {self.model}", provider="openai", original_error=e)
        except openai.APIConnectionError as e:
            raise ConnectionError("Cannot reach OpenAI API", provider="openai", original_error=e)
        except openai.APIError as e:
            raise ProviderApiError(str(e), provider="openai", original_error=e)

    def _build_request_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "instructions": self.instructions,
            "input": [c.model_dump() for c in self.conversation_history],
        }
        tools: list[OpenAiToolSchema] | None = self._get_tools()
        if tools:
            kwargs["tools"] = tools
        return kwargs

    def _extract_tool_calls(self, response: Response) -> list[ResponseFunctionToolCall]:
        return [item for item in response.output if item.type == "function_call"]

    def _extract_text(self, response: Response) -> str:
        return response.output_text

    def _execute_tool_call(self, tool_call: ResponseFunctionToolCall) -> None:
        tool_request_text: str = f"[Tool call: {tool_call.name}({tool_call.arguments})]"

        self.conversation_history.append(
            Conversation(role="assistant", content=tool_request_text)
        )
        print(tool_request_text)

        result: str = self.tool_registry.execute(tool_call.name, tool_call.arguments)
        tool_response_text: str = f"[Tool result: {result}]"

        self.conversation_history.append(
            Conversation(role="user", content=tool_response_text)
        )
        print(tool_response_text)

    def _get_tools(self) -> list[OpenAiToolSchema] | None:
        if not self.tool_registry.tool_spec:
            return None
        return [
            OpenAiToolSchema(
                type="function",
                name=spec["name"],
                description=spec.get("description"),
                parameters=spec["parameters"],
                strict=None,
            )
            for spec in self.tool_registry.tool_spec.values()
        ]


class AsyncOpenAICompatClient(AsyncBaseLLMClient, ABC):
    """Async base for any provider using the OpenAI-compatible API."""

    async def _call_api(self, **kwargs: Any) -> Response:
        try:
            return await self.client.responses.create(**kwargs)
        except openai.AuthenticationError as e:
            raise AuthenticationError("Invalid API key", provider="openai", original_error=e)
        except openai.RateLimitError as e:
            raise RateLimitExceededError("Rate limit exceeded", provider="openai", original_error=e)
        except openai.NotFoundError as e:
            raise ModelNotFoundError(f"Model not found: {self.model}", provider="openai", original_error=e)
        except openai.APIConnectionError as e:
            raise ConnectionError("Cannot reach OpenAI API", provider="openai", original_error=e)
        except openai.APIError as e:
            raise ProviderApiError(str(e), provider="openai", original_error=e)

    def _build_request_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "instructions": self.instructions,
            "input": [c.model_dump() for c in self.conversation_history],
        }
        tools: list[OpenAiToolSchema] | None = self._get_tools()
        if tools:
            kwargs["tools"] = tools
        return kwargs

    def _extract_tool_calls(self, response: Response) -> list[ResponseFunctionToolCall]:
        return [item for item in response.output if item.type == "function_call"]

    def _extract_text(self, response: Response) -> str:
        return response.output_text

    def _execute_tool_call(self, tool_call: ResponseFunctionToolCall) -> None:
        tool_request_text: str = f"[Tool call: {tool_call.name}({tool_call.arguments})]"

        self.conversation_history.append(
            Conversation(role="assistant", content=tool_request_text)
        )
        print(tool_request_text)

        result: str = self.tool_registry.execute(tool_call.name, tool_call.arguments)
        tool_response_text: str = f"[Tool result: {result}]"

        self.conversation_history.append(
            Conversation(role="user", content=tool_response_text)
        )
        print(tool_response_text)

    def _get_tools(self) -> list[OpenAiToolSchema] | None:
        if not self.tool_registry.tool_spec:
            return None
        return [
            OpenAiToolSchema(
                type="function",
                name=spec["name"],
                description=spec.get("description"),
                parameters=spec["parameters"],
                strict=None,
            )
            for spec in self.tool_registry.tool_spec.values()
        ]
