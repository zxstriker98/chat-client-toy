from __future__ import annotations

from openai.types.responses import FunctionToolParam
from pydantic import BaseModel
from typing import Any, Literal, Union

# Type alias — OpenAI's FunctionToolParam is already a TypedDict with
# type, name, description, parameters, and strict fields.
OpenAIToolSchema = FunctionToolParam


class Conversation(BaseModel):
    role: Literal["user", "assistant"]
    content: Union[str, list[Any]]


class AnthropicToolSchema(BaseModel):
    """Tool schema for Anthropic's tool use API."""
    name: str
    description: str
    input_schema: Any
