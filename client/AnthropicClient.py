from typing import Any
from client.base import BaseLLMClient
from anthropic import Anthropic
from anthropic.types import Message, ToolUseBlock
from client.models import Conversation

MAX_TOKENS: int = 4096

class AnthropicClient(BaseLLMClient):
    def _create_client(self) -> Anthropic:
        return Anthropic()
    
    def _build_request_kwargs(self) -> dict[str, Any]:
        kwargs = {
            "model": self.model,
            "system": self.instructions,
            "messages": self.conversation_history.model_dump()["conversations"],
            "max_tokens": MAX_TOKENS
        }
        tools = self._get_tools()
        if tools:
            kwargs["tools"] = tools
        return kwargs

    def _get_tools(self) -> None | list[dict]:
        if not self.tool_registry.tool_spec:
            return None
        return [
            {
                "name": spec["name"],
                "description": spec.get("description", ""),
                "input_schema": spec["parameters"],
            } for spec in self.tool_registry.tool_spec.values()
        ]
    
    def _call_api(self, **kwargs: Any) -> Message:
        return self.client.messages.create(**kwargs)
    
    def _extract_tool_calls(self, response: Message) -> list[ToolUseBlock]:
        return [block for block in response.content if block.type == "tool_use"]
    
    def _extract_text(self, response: Message) -> str:
        text_blocks = [block.text for block in response.content if block.type == "text"]
        return "\n".join(text_blocks)
    
    def generate_response(self, query: str) -> str:
        self.conversation_history.append_user_query(query)

        while True:
            kwargs: dict[str, Any] = self._build_request_kwargs()
            response: Message = self._call_api(**kwargs)

            tool_calls = self._extract_tool_calls(response)

            if not tool_calls:
                return self._process_text_response(self._extract_text(response))

            self._append_assistant_tool_use(response)

            for tool_call in tool_calls:
                self._execute_tool_call(tool_call)

        return ""

    def _append_assistant_tool_use(self, response: Message) -> None:
        content = [block.model_dump() for block in response.content]
        self.conversation_history.conversations.append(
            Conversation(role="assistant", content=content)
        )

    def _execute_tool_call(self, tool_call: ToolUseBlock) -> None:
        import json
        arguments = json.dumps(tool_call.input)
        tool_request_text = f"[Tool call: {tool_call.name}({arguments})]"
        print(tool_request_text)

        result = self.tool_registry.execute(tool_call.name, arguments=arguments)
        tool_response_text: str = f"[Tool result: {result}]"
        print(tool_response_text)

        self.conversation_history.conversations.append(
            Conversation(role="user", content=[
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": str(result),
                }
            ])
        )