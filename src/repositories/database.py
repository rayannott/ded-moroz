import pendulum
from loguru import logger
from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from src.models.room import Room
from src.models.user import User
from src.repositories.orm.converters import room, user
from src.repositories.orm.models import Base, RoomORM, UserORM
from src.shared.exceptions import (
    AlreadyInRoom,
    MaxNumberOfRoomsReached,
    NotInRoom,
    RoomNotFound,
    UserAlreadyExists,
    UserNotFound,
)
from src.shared.random_utils import random_code


class DatabaseRepository:
    def __init__(self, engine: Engine):
        self.engine = engine
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(engine)

    def create_room(self, created_by_user_id: int, room_name: str) -> Room:
        logger.debug(f"Creating room {room_name!r} by user id={created_by_user_id}")
        _ = self.get_user(user_id=created_by_user_id)  # raises if not found

        room_id = random_code()
        now = DateTime.utcnow()

        room_orm = RoomORM(
            id=room_id,
            name=room_name,
            manager_user_id=created_by_user_id,
            created_dt=now.naive(),
        )

        with self.session() as s:
            s.add(room_orm)
            s.commit()

        logger.debug(f"Add room {room_orm}")

        return Room(
            id=room_id,
            name=room_name,
            manager_user_id=created_by_user_id,
            created_dt=now,
        )

    def create_user(self, id: int, username: str | None, name: str | None) -> User:
        with self.session() as s:
            if s.get(UserORM, id) is not None:
                raise UserAlreadyExists(f"User with id={id} already exists")

            user_orm = UserORM(id=id, username=username, name=name)
            s.add(user_orm)
            s.commit()
            logger.debug(f"Add user {user_orm}")
            return User(id=id, username=username, name=name)

    def get_room(self, room_id: str) -> Room:
        with self.session() as s:
            room_orm = s.get(RoomORM, room_id)
        if room_orm is None:
            raise RoomNotFound(f"Room with id={room_id} not found")
        logger.debug(f"Get room {room_orm}")
        return room(room_orm)

    def get_user(self, user_id: int) -> User:
        with self.session() as s:
            user_orm = s.get(UserORM, user_id)
            if user_orm is None:
                raise UserNotFound(f"User with id={user_id} not found")
            logger.debug(f"Get user {user_orm}")
            return user(user_orm)

    def get_rooms_managed_by_user(self, user_id: int) -> list[Room]:
        # raises UserNotFound
        _ = self.get_user(user_id=user_id)  # raises if not found

        with self.session() as s:
            room_orms = (
                s.query(RoomORM).filter(RoomORM.manager_user_id == user_id).all()
            )
        logger.debug(f"Get rooms managed by user id={user_id}: {room_orms}")
        return [room(room_orm) for room_orm in room_orms]

    def get_active_rooms_managed_by_user(self, user_id: int) -> list[Room]:
        # raises UserNotFound
        all_rooms = self.get_rooms_managed_by_user(user_id=user_id)
        return [room for room in all_rooms if room.is_active()]

    def get_users_in_room(self, room_id: str) -> list[User]:
        _ = self.get_room(room_id=room_id)  # raises if not found

        with self.session() as s:
            user_orms = s.query(UserORM).filter(UserORM.room_id == room_id).all()
        logger.debug(f"Get users in room id={room_id}: {user_orms}")
        return [user(user_orm) for user_orm in user_orms]

    def join_room(self, user_id: int, room_id: str):
        # raises UserNotFound, AlreadyInRoom, RoomNotFound
        with self.session() as s:
            user_orm = s.get(UserORM, user_id)
            if user_orm is None:
                raise UserNotFound(f"User with id={user_id} not found")
            if user_orm.room_id == room_id:
                raise AlreadyInRoom(
                    f"User id={user_id} is already in room id={room_id}"
                )
            user_orm.room_id = room_id
            s.commit()
            logger.debug(f"User id={user_id} joined room id={room_id}")

    def delete_room(self, room_id: str):
        # raises RoomNotFound
        with self.session() as s:
            room_orm = s.get(RoomORM, room_id)
            if room_orm is None:
                raise RoomNotFound(f"Room with id={room_id} not found")
            s.delete(room_orm)
            s.commit()
            logger.debug(f"Deleted room id={room_id}")

    def leave_room(self, user_id: int):
        # raises UserNotFound, NotInRoom
        with self.session() as s:
            user_orm = s.get(UserORM, user_id)
            if user_orm is None:
                raise UserNotFound(f"User with id={user_id} not found")
            if (r_id := user_orm.room_id) is not None:
                raise NotInRoom(f"User id={user_id} is not in any room")
            user_orm.room_id = None
            s.commit()
            logger.debug(f"User id={user_id} left room id={r_id}")

    def set_user_name(self, user_id: int, name: str):
        # raises UserNotFound
        with self.session() as s:
            user_orm = s.get(UserORM, user_id)
            if user_orm is None:
                raise UserNotFound(f"User with id={user_id} not found")
            user_orm.name = name
            s.commit()
            logger.debug(f"Set user id={user_id} name={name}")
