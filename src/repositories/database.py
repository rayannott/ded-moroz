from loguru import logger
from pydantic_extra_types.pendulum_dt import DateTime

from src.models.room import Room
from src.models.user import User
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
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def _reraise_user_not_found(self, user_id: int):
        raise UserNotFound(f"User with id={user_id} not found")

    def create_room(self, created_by_user_id: int, room_name: str) -> Room:
        logger.debug(f"Creating room {room_name!r} by user id={created_by_user_id}")
        _ = self.get_user(user_id=created_by_user_id)

        room = Room(
            id=random_code(),
            name=room_name,
            manager_user_id=created_by_user_id,
            created_dt=DateTime.utcnow(),
        )
        # TODO populate the database
        # raises UserNotFound
        return room

    def create_user(
        self,
        id: int,
        username: str | None,
        name: str | None,
    ) -> User:
        user = User(
            id=id,
            username=username,
            name=name,
        )
        # TODO populate the database
        # raises UserAlreadyExists
        return user

    def get_room(self, room_id: int) -> Room:
        # TODO implement
        # raises RoomNotFound
        pass

    def get_user(self, user_id: int) -> User:
        # TODO implement
        # raises UserNotFound
        raise UserNotFound()

    def get_rooms_managed_by_user(self, user_id: int) -> list[Room]:
        # TODO implement
        # raises UserNotFound
        return []

    def get_active_rooms_managed_by_user(self, user_id: int) -> list[Room]:
        # raises UserNotFound
        all_rooms = self.get_rooms_managed_by_user(user_id=user_id)
        return [room for room in all_rooms if room.is_active()]

    def get_users_in_room(self, room_id: int) -> list[User]:
        # TODO implement
        # raises RoomNotFound
        return []

    def join_room(self, user_id: int, room_id: int):
        # TODO implement
        # raises AlreadyInRoom, RoomNotFound
        return None

    def leave_room(self, user_id: int, room_id: int):
        # TODO implement
        # raises UserNotFound, RoomNotFound, NotInRoom
        pass

    def set_user_name(self, user_id: int, name: str):
        # TODO implement
        # raises UserNotFound
        pass
