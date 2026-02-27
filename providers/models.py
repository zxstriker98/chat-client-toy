from __future__ import annotations

from openai.types.responses import FunctionToolParam
from pydantic import BaseModel
from typing import Any, Literal, Union


class Conversation(BaseModel):
    role: Literal["user", "assistant"]
    content: Union[str, list[Any]]


class OpenAiToolSchema(BaseModel, FunctionToolParam):
    """Type-safe wrapper around OpenAI's FunctionToolParam."""
    pass

class AnthropicToolSchema(BaseModel):
    """Tool schema for Anthropic's tool use API."""
    name: str
    description: str
    input_schema: Any
