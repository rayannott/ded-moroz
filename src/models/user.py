from typing import Optional

from pydantic import AwareDatetime
from pydantic_extra_types.pendulum_dt import DateTime as Dt
from sqlmodel import Column, DateTime, Field, SQLModel


class User(SQLModel, table=True):  # type: ignore[call-arg]
    id: int = Field(primary_key=True)
    joined_dt: AwareDatetime = Field(
        default_factory=Dt.utcnow,
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

    @property
    def formal_display_name(self) -> str:
        return (
            f"{self.display_name} (@{self.username})"
            if self.username
            else self.display_name
        )
