from __future__ import annotations
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
