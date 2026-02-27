from __future__ import annotations

from openai.types.responses import FunctionToolParam
from pydantic import BaseModel
from typing import Any, Literal, Union


class Conversation(BaseModel):
    role: Literal["user", "assistant"]
    content: Union[str, list[Any]]


class ConversationHistory(BaseModel):
    conversations: list[Conversation]

    def append_user_query(self, user_input: str) -> None:
        self.conversations.append(Conversation(role="user", content=user_input))

    def append_assistant_response(self, output: str) -> None:
        self.conversations.append(Conversation(role="assistant", content=output))

class OpenAiToolSchema(BaseModel, FunctionToolParam):
    """Type-safe wrapper around OpenAI's FunctionToolParam."""
    pass

class AnthropicToolSchema(BaseModel):
    """Tool schema for Anthropic's tool use API."""
    name: str
    description: str
    input_schema: Any
