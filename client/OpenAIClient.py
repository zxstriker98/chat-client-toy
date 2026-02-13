from openai import OpenAI, AsyncOpenAI, Stream, AsyncStream
from openai.types.responses import Response, ResponseStreamEvent, FunctionToolParam, ResponseFunctionToolCall
from pydantic import BaseModel
from typing import Any, Literal
from tools.tools import ToolRegistry

class Conversation(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ConversationHistory(BaseModel):
    conversations: list[Conversation]

    def append_user_query(self, user_input: str) -> None:
        self.conversations.append(Conversation(role="user", content=user_input))

    def append_assistant_response(self, output: str) -> None:
        self.conversations.append(Conversation(role="assistant", content=output))

class OpenAIClient(BaseModel):
    client: OpenAI
    model: Literal["gpt-5.2"]
    conversation_history: ConversationHistory
    instructions: str
    tool_registry: ToolRegistry

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, model: str, instructions: str, tool_registry: ToolRegistry = ToolRegistry()) -> None:
        super().__init__(
            client=OpenAI(),
            model=model,
            instructions=instructions,
            conversation_history=ConversationHistory(conversations=[]),
            tool_registry=tool_registry)

    def generate_response(self, query: str) -> str:
        self.conversation_history.append_user_query(query)

        while True:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "instructions": self.instructions,
                "input": self.conversation_history.model_dump()["conversations"],
            }
            tools: list[FunctionToolParam] | None = self._get_tools()
            if tools:
                kwargs["tools"] = tools

            response: Response = self.client.responses.create(**kwargs)

            tool_calls: list[ResponseFunctionToolCall] = [
                item for item in response.output if item.type == "function_call"
            ]

            if not tool_calls:
                text: str = response.output_text
                print(text)
                self.conversation_history.append_assistant_response(text)
                return text

            for tool_call in tool_calls:
                result: str = self.tool_registry.execute(tool_call.name, tool_call.arguments)

                self.conversation_history.conversations.append(
                    Conversation(role="assistant", content=f"[Tool call: {tool_call.name}({tool_call.arguments})]")
                )
                self.conversation_history.conversations.append(
                    Conversation(role="user", content=f"[Tool result: {result}]")
                )

        return ""

    def _get_tools(self) -> list[FunctionToolParam] | None:
        if not self.tool_registry.tool_spec:
            return None
        return [
            FunctionToolParam(
                type="function",
                name=spec["name"],
                description=spec.get("description"),
                parameters=spec["parameters"],
                strict=None,
            )
            for spec in self.tool_registry.tool_spec.values()
        ]

class AsyncOpenAIClient(BaseModel):
    client: AsyncOpenAI
    model: Literal["gpt-5.2"]
    conversation_history: ConversationHistory
    instructions: str
    tool_registry: ToolRegistry

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, model: str, instructions: str, tool_registry: ToolRegistry = ToolRegistry()) -> None:
        super().__init__(
            client=AsyncOpenAI(),
            model=model,
            instructions=instructions,
            conversation_history=ConversationHistory(conversations=[]),
            tool_registry=tool_registry)

    async def generate_response(self, query: str) -> str:
        self.conversation_history.append_user_query(query)

        while True:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "instructions": self.instructions,
                "input": self.conversation_history.model_dump()["conversations"],
            }
            tools: list[FunctionToolParam] | None = self._get_tools()
            if tools:
                kwargs["tools"] = tools

            response: Response = await self.client.responses.create(**kwargs)

            tool_calls: list[ResponseFunctionToolCall] = [
                item for item in response.output if item.type == "function_call"
            ]

            if not tool_calls:
                text: str = response.output_text
                print(text)
                self.conversation_history.append_assistant_response(text)
                return text

            for tool_call in tool_calls:
                result: str = self.tool_registry.execute(tool_call.name, tool_call.arguments)

                self.conversation_history.conversations.append(
                    Conversation(role="assistant", content=f"[Tool call: {tool_call.name}({tool_call.arguments})]")
                )
                self.conversation_history.conversations.append(
                    Conversation(role="user", content=f"[Tool result: {result}]")
                )

        return ""

    def _get_tools(self) -> list[FunctionToolParam] | None:
        if not self.tool_registry.tool_spec:
            return None
        return [
            FunctionToolParam(
                type="function",
                name=spec["name"],
                description=spec.get("description"),
                parameters=spec["parameters"],
                strict=None,
            )
            for spec in self.tool_registry.tool_spec.values()
        ]
