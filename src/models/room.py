from typing import TYPE_CHECKING, Optional

from pydantic import AwareDatetime
from sqlmodel import Column, Field, Integer, Relationship, SQLModel
from sqlmodel import DateTime

from src.shared.times import utcnow

if TYPE_CHECKING:
    from src.models.user import User


class Room(SQLModel, table=True):
    id: str = Field(primary_key=True, description="Room ID (hex string)")
    short_code: int = Field(sa_column=Column(Integer, nullable=False, index=True))
    name: str = Field(nullable=False)

    manager_user_id: int = Field(foreign_key="user.id", nullable=False)

    created_dt: AwareDatetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=utcnow,
    )
    started_at: Optional[AwareDatetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    completed_dt: Optional[AwareDatetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    # relationships
    manager: Optional["User"] = Relationship(
        back_populates="managed_rooms",
        sa_relationship_kwargs=dict(foreign_keys="[Room.manager_user_id]"),
    )

    players: list["User"] = Relationship(
        back_populates="room",
        sa_relationship_kwargs=dict(foreign_keys="[User.room_id]"),
    )

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
