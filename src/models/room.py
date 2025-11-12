from typing import Optional

from pydantic import AwareDatetime
from pydantic_extra_types.pendulum_dt import DateTime as Dt
from sqlmodel import Column, DateTime, Field, Integer, SQLModel


class Room(SQLModel, table=True):  # type: ignore[call-arg]
    id: str = Field(primary_key=True, description="Room ID (hex string)")
    short_code: int = Field(sa_column=Column(Integer, nullable=False, index=True))
    name: str = Field(nullable=False)

    manager_user_id: int = Field(foreign_key="user.id", nullable=False)

    created_dt: AwareDatetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=Dt.utcnow,
    )
    started_dt: Optional[AwareDatetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    completed_dt: Optional[AwareDatetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    def is_active(self) -> bool:
        return self.completed_dt is None

    @property
    def display_short_code(self) -> str:
        return f"{self.short_code:04d}"

    @property
    def game_started(self) -> bool:
        return self.started_dt is not None

    @property
    def game_completed(self) -> bool:
        return self.completed_dt is not None
