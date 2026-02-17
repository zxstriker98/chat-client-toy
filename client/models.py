from pydantic import BaseModel
from typing import Literal


class Conversation(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ConversationHistory(BaseModel):
    conversations: list[Conversation]

    def append_user_query(self, user_input: str) -> None:
        self.conversations.append(Conversation(role="user", content=user_input))

    def append_assistant_response(self, output: str) -> None:
        self.conversations.append(Conversation(role="assistant", content=output))
