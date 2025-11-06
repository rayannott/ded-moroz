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


class DatabaseRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_room(self, created_by_user_id: int, room_name: str) -> Room:
        room = Room(
            id=1234,
            name=room_name,
            manager_user_id=created_by_user_id,
            created_dt=DateTime.utcnow(),
        )
        # TODO populate the database
        # raises MaxNumberOfRoomsReached, UserNotFound
        return room

    def create_user(self, id: int, username: str, name: str) -> User:
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
        pass

    def get_rooms_managed_by_user(self, user_id: int) -> list[Room]:
        # TODO implement
        # raises UserNotFound
        return []

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
