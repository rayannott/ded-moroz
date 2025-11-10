from typing import Optional

from pydantic import AwareDatetime
from sqlmodel import Column, DateTime, Field, SQLModel

from src.shared.times import utcnow


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    joined_dt: AwareDatetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    name: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)

    room_id: Optional[str] = Field(default=None, foreign_key="room.id")

    def __str__(self) -> str:
        _in_room = f" (in room {self.room_id})" if self.room_id else ""
        return f"User(id={self.id}; @{self.username}, {self.name}){_in_room}"

    @property
    def display_name(self) -> str:
        return self.name or self.username or "Unknown"
