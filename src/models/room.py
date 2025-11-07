from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime


class Room(BaseModel):
    id: str
    name: str
    manager_user_id: int
    created_dt: DateTime
    completed_dt: DateTime | None = None

    def is_active(self) -> bool:
        return self.completed_dt is None

    @property
    def short_code(self) -> int:
        """Return a short numeric code for the room for easier sharing."""
        return int(self.id, 16) % 10_000
