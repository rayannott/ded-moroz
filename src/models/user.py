from datetime import datetime
from typing import TYPE_CHECKING, Optional
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime as DateTime
from sqlalchemy import DateTime as SADateTime
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.room import Room


def utcnow() -> datetime:
    return datetime.now(tz=ZoneInfo("UTC"))


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: int = Field(primary_key=True)
    joined_dt: DateTime = Field(
        default_factory=utcnow,
        sa_column=Column(SADateTime(timezone=True), nullable=False),
    )
    name: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)

    # simple membership: a user may be in at most one room
    room_id: Optional[str] = Field(default=None, foreign_key="rooms.id")
    room: Optional["Room"] = Relationship(back_populates="members")

    def __str__(self) -> str:
        _in_room = f" (in room {self.room_id})" if self.room_id else ""
        return f"User(id={self.id}; @{self.username}, {self.name}){_in_room}"

    @property
    def display_name(self) -> str:
        return self.name or self.username or "Unknown"
