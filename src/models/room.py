from datetime import datetime, timezone
from typing import Optional

from pydantic import AwareDatetime
from sqlmodel import Column, Field, Integer, SQLModel

from src.models._types import UTCDateTime


class Room(SQLModel, table=True):  # type: ignore[call-arg]
    id: str = Field(primary_key=True, description="Room ID (hex string)")
    short_code: int = Field(sa_column=Column(Integer, nullable=False, index=True))

    manager_user_id: int = Field(foreign_key="user.id", nullable=False)

    created_dt: AwareDatetime = Field(
        sa_column=Column(UTCDateTime(), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    started_dt: Optional[AwareDatetime] = Field(
        default=None, sa_column=Column(UTCDateTime(), nullable=True)
    )
    completed_dt: Optional[AwareDatetime] = Field(
        default=None, sa_column=Column(UTCDateTime(), nullable=True)
    )

    @property
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
