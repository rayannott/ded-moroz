from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime


class Room(BaseModel):
    id: int
    name: str
    manager_user_id: int
    created_dt: DateTime
    completed_dt: DateTime | None = None

    def is_active(self) -> bool:
        return self.completed_dt is None
