from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime


class Room(BaseModel):
    code: int
    name: str
    created_dt: DateTime
    completed_dt: DateTime | None = None
