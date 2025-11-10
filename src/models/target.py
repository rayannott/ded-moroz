from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.user import User


class Target(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: str = Field(foreign_key="rooms.id", nullable=False)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    target_user_id: int = Field(foreign_key="users.id", nullable=False)

    user: "User" = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="[Target.user_id]")
    )
    target_user: "User" = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="[Target.target_user_id]")
    )
