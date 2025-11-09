from pydantic import BaseModel
from telebot import types


class User(BaseModel):
    id: int
    name: str | None
    username: str | None = None
    room_id: str | None = None

    def __str__(self) -> str:
        _in_room = f" (in room {self.room_id})" if self.room_id else ""
        return f"User(id={self.id}; @{self.username}, {self.name}){_in_room}"

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
