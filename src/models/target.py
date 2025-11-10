from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from src.models.room import Room
from src.models.user import User


class Target(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: str = Field(foreign_key="room.id", nullable=False)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    target_user_id: int = Field(foreign_key="user.id", nullable=False)

    # relationships
    room: Optional["Room"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="[Target.room_id]")
    )
    user: Optional["User"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="[Target.user_id]")
    )
    target_user: Optional["User"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="[Target.target_user_id]")
    )
