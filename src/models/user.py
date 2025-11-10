from typing import TYPE_CHECKING, Optional

from pydantic import AwareDatetime
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from src.shared.times import utcnow

if TYPE_CHECKING:
    from src.models.room import Room


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    joined_dt: AwareDatetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    name: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)

    room_id: Optional[str] = Field(default=None, foreign_key="room.id")

    # relationships
    room: Optional["Room"] = Relationship(
        back_populates="players",
        sa_relationship_kwargs=dict(foreign_keys="[User.room_id]"),
    )

    managed_rooms: list["Room"] = Relationship(
        back_populates="manager",
        sa_relationship_kwargs=dict(foreign_keys="[Room.manager_user_id]"),
    )

    def __str__(self) -> str:
        _in_room = f" (in room {self.room_id})" if self.room_id else ""
        return f"User(id={self.id}; @{self.username}, {self.name}){_in_room}"

    @property
    def display_name(self) -> str:
        return self.name or self.username or "Unknown"
