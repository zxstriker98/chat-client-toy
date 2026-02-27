import json
from typing import Any
from providers.base import BaseLLMClient, AsyncBaseLLMClient
from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import Message, ToolUseBlock
from providers.models import Conversation, AnthropicToolSchema

MAX_TOKENS: int = 4096

class AnthropicClient(BaseLLMClient):
    def _create_client(self) -> Anthropic:
        return Anthropic()

    def _build_request_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "system": self.instructions,
            "messages": [c.model_dump() for c in self.conversation_history],
            "max_tokens": MAX_TOKENS,
        }
        tools: list[AnthropicToolSchema] | None = self._get_tools()
        if tools:
            kwargs["tools"] = [tool.model_dump() for tool in tools]
        return kwargs

    def _get_tools(self) -> list[AnthropicToolSchema] | None:
        if not self.tool_registry.tool_spec:
            return None
        return [
            AnthropicToolSchema(
                name=spec["name"],
                description=spec.get("description", ""),
                input_schema=spec["parameters"],
            )
            for spec in self.tool_registry.tool_spec.values()
        ]

    def _call_api(self, **kwargs: Any) -> Message:
        return self.client.messages.create(**kwargs)

    def _extract_tool_calls(self, response: Message) -> list[ToolUseBlock]:
        return [block for block in response.content if block.type == "tool_use"]

    def _extract_text(self, response: Message) -> str:
        text_blocks: list[str] = [block.text for block in response.content if block.type == "text"]
        return "\n".join(text_blocks)

    def _pre_tool_hook(self, response: Message) -> None:
        content: list[dict[str, Any]] = [block.model_dump() for block in response.content]
        self.conversation_history.append(
            Conversation(role="assistant", content=content)
        )

    def _execute_tool_call(self, tool_call: ToolUseBlock) -> None:
        arguments: str = json.dumps(tool_call.input)
        tool_request_text: str = f"[Tool call: {tool_call.name}({arguments})]"
        print(tool_request_text)

        result: str = self.tool_registry.execute(tool_call.name, arguments=arguments)
        tool_response_text: str = f"[Tool result: {result}]"
        print(tool_response_text)

        self.conversation_history.append(
            Conversation(role="user", content=[
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": str(result),
                }
            ])
        )


class AsyncAnthropicClient(AsyncBaseLLMClient):
    def _create_client(self) -> AsyncAnthropic:
        return AsyncAnthropic()

    def _build_request_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "system": self.instructions,
            "messages": [c.model_dump() for c in self.conversation_history],
            "max_tokens": MAX_TOKENS,
        }
        tools: list[AnthropicToolSchema] | None = self._get_tools()
        if tools:
            kwargs["tools"] = [tool.model_dump() for tool in tools]
        return kwargs

    def _get_tools(self) -> list[AnthropicToolSchema] | None:
        if not self.tool_registry.tool_spec:
            return None
        return [
            AnthropicToolSchema(
                name=spec["name"],
                description=spec.get("description", ""),
                input_schema=spec["parameters"],
            )
            for spec in self.tool_registry.tool_spec.values()
        ]

    async def _call_api(self, **kwargs: Any) -> Message:
        return await self.client.messages.create(**kwargs)

    def _extract_tool_calls(self, response: Message) -> list[ToolUseBlock]:
        return [block for block in response.content if block.type == "tool_use"]

    def _extract_text(self, response: Message) -> str:
        text_blocks: list[str] = [block.text for block in response.content if block.type == "text"]
        return "\n".join(text_blocks)

    def _pre_tool_hook(self, response: Message) -> None:
        """Append the full assistant response (including tool_use blocks) to history."""
        content: list[dict[str, Any]] = [block.model_dump() for block in response.content]
        self.conversation_history.append(
            Conversation(role="assistant", content=content)
        )

    def _execute_tool_call(self, tool_call: ToolUseBlock) -> None:
        arguments: str = json.dumps(tool_call.input)
        tool_request_text: str = f"[Tool call: {tool_call.name}({arguments})]"
        print(tool_request_text)

        result: str = self.tool_registry.execute(tool_call.name, arguments=arguments)
        tool_response_text: str = f"[Tool result: {result}]"
        print(tool_response_text)

        self.conversation_history.append(
            Conversation(role="user", content=[
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": str(result),
                }
            ])
        )