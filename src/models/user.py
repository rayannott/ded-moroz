from pydantic import BaseModel
from telebot import types


class User(BaseModel):
    id: int
    username: str | None = None
    name: str | None = None
    target_user_id: int | None = None

    def __str__(self) -> str:
        return f"User(id={self.id}; @{self.username}, {self.name})"

    @classmethod
    def from_message(cls, message: types.Message) -> "User":
        return User(
            id=message.chat.id,
            username=message.chat.username,
            name=message.chat.first_name,
        )
