from pydantic_extra_types.pendulum_dt import DateTime

from src.models.room import Room
from src.models.user import User
from src.repositories.orm.models import Base, RoomORM, UserORM


def room(room_orm: RoomORM) -> Room:
    return Room(
        id=room_orm.id,
        name=room_orm.name,
        manager_user_id=room_orm.manager_user_id,
        created_dt=DateTime.fromisoformat(room_orm.created_dt.isoformat()),
        completed_dt=(
            DateTime.fromisoformat(room_orm.completed_dt.isoformat())
            if room_orm.completed_dt
            else None
        ),
    )


def user(user_orm: UserORM) -> User:
    return User(
        id=user_orm.id,
        username=user_orm.username,
        name=user_orm.name,
        room_id=user_orm.room_id,
    )
