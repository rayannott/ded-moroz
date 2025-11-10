from typing import Optional

from sqlmodel import Field, SQLModel


class Target(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: str = Field(foreign_key="room.id", nullable=False)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    target_user_id: int = Field(foreign_key="user.id", nullable=False)
