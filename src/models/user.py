from pydantic import BaseModel
from telebot import types


class User(BaseModel):
    id: int
    name: str | None
    username: str | None = None

    def __str__(self) -> str:
        return (
            f"User(id={self.id}; @{self.username}, {self.name})"
        )

    @classmethod
    def from_message(cls, message: types.Message) -> "User":
        return User(
            id=message.from_user.id if message.from_user else 0,
            name=message.chat.first_name,
            username=message.chat.username,
        )

    @property
    def display_name(self) -> str:
        return self.name or self.username or "Unknown"
