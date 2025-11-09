from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic_extra_types.pendulum_dt import DateTime


class Room(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    manager_user_id: int
    created_dt: DateTime
    started_at: DateTime | None = None
    completed_dt: DateTime | None = None

    def is_active(self) -> bool:
        return self.completed_dt is None

    @property
    def short_code(self) -> int:
        """Return a short numeric code for the room for easier sharing."""
        return int(self.id, 16) % 10_000

    @property
    def display_short_code(self) -> str:
        """Return a zero-padded short code for display purposes."""
        return f"{self.short_code:04d}"

    @property
    def game_started(self) -> bool:
        return self.started_at is not None

    @property
    def game_completed(self) -> bool:
        return self.completed_dt is not None

    @field_validator("created_dt", "started_at", "completed_dt", mode="before")
    @classmethod
    def convert_std_datetime_to_pendulum(cls, v):
        if isinstance(v, datetime):
            return DateTime.fromisoformat(v.isoformat())
        if v is None:
            return None
        return v
