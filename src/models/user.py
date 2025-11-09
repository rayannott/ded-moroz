from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_extra_types.pendulum_dt import DateTime
from telebot import types


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    joined_dt: DateTime = Field(default_factory=DateTime.utcnow)
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

    @field_validator("joined_dt", mode="before")
    @classmethod
    def convert_std_datetime_to_pendulum(cls, v):
        if isinstance(v, datetime):
            return DateTime.fromisoformat(v.isoformat())
        if v is None:
            return None
        return v
