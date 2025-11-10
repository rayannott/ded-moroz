from datetime import datetime
from typing import TYPE_CHECKING, Optional
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime as DateTime
from sqlalchemy import DateTime as SADateTime
from sqlalchemy import Integer
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.user import User


def utcnow() -> datetime:
    return datetime.now(tz=ZoneInfo("UTC"))


class Room(SQLModel, table=True):
    __tablename__ = "rooms"  # type: ignore

    id: str = Field(primary_key=True, description="Room ID (hex string)")
    short_code: int = Field(sa_column=Column(Integer, nullable=False, index=True))
    name: str = Field(nullable=False)

    manager_user_id: int = Field(foreign_key="users.id", nullable=False)

    created_dt: DateTime = Field(
        sa_column=Column(SADateTime(timezone=True), nullable=False),
        default_factory=utcnow,
    )
    started_at: Optional[DateTime] = Field(
        default=None, sa_column=Column(SADateTime(timezone=True), nullable=True)
    )
    completed_dt: Optional[DateTime] = Field(
        default=None, sa_column=Column(SADateTime(timezone=True), nullable=True)
    )

    members: list["User"] = Relationship(back_populates="room")

    def is_active(self) -> bool:
        return self.completed_dt is None

    @property
    def display_short_code(self) -> str:
        return f"{self.short_code:04d}"

    @property
    def game_started(self) -> bool:
        return self.started_at is not None

    @property
    def game_completed(self) -> bool:
        return self.completed_dt is not None
