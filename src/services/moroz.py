from loguru import logger

from src.models.room import Room
from src.repositories.database import DatabaseRepository
from src.settings import Settings
from src.models.user import User
from src.shared.exceptions import (
    MaxNumberOfRoomsReached,
    AlreadyInRoom,
    UserNotFound,
    NotInRoom,
    RoomNotFound,
)


class Moroz:
    """The main game logic."""

    def __init__(
        self,
        database_repository: DatabaseRepository,
        max_rooms_managed_by_user: int,
    ):
        self.database_repository = database_repository
        self.max_rooms_managed_by_user = max_rooms_managed_by_user

    def create_room(self, created_by_user_id: int, room_name: str) -> Room:
        """Create a new room managed by the given user
        and return it.

        Raises
            `MaxNumberOfRoomsReached` if the user already manages
                the maximum allowed number of rooms
            `UserNotFound` if the user does not exist
        """
        logger.info(f"Creating room {room_name!r} by user id={created_by_user_id}")
        active_managed_rooms = (
            self.database_repository.get_active_rooms_managed_by_user(
                user_id=created_by_user_id
            )
        )
        if len(active_managed_rooms) >= self.max_rooms_managed_by_user:
            raise MaxNumberOfRoomsReached(
                f"User {created_by_user_id} already manages "
                f"{len(active_managed_rooms)} rooms, "
                f"the maximum allowed number is "
                f"{self.max_rooms_managed_by_user}"
            )
        room = self.database_repository.create_room(
            created_by_user_id=created_by_user_id,
            room_name=room_name,
        )
        logger.info(f"Room created {room}")
        return room

    def delete_room(self, user: User, room_id: str):
        """Delete the given room if the user is its manager.

        Raises
            `UserNotFound` if the acting user does not exist (critical)
            `RoomNotFound` if the room does not exist
        """
        logger.info(f"Deleting room id={room_id} by its manager")
        user_actual = self.database_repository.get_user(
            user.id
        )  # TODO do I need this check?
        self.database_repository.delete_room(
            room_id=room_id,
        )
        logger.info(f"Room deleted: {room_id} by user {user_actual}")

    def join_room_by_short_code(self, user: User, room_short_code: int):
        """Join the user to the given room.

        Raises
            `RoomNotFound` if the room does not exist
            `AlreadyInRoom` if the user is already in some room
            `UserNotFound` if the user does not exist
        """
        logger.info(f"User {user} joining {room_short_code=}")
        user_orm = self.database_repository.get_user(user.id)
        if user_orm.room_id is not None:
            raise AlreadyInRoom(
                f"User {user.id=} is already in room id={user_orm.room_id}"
            )
        room = self.database_repository.get_room_by_short_code(room_short_code)
        self.database_repository.join_room(
            user_id=user.id,
            room_id=room.id,
        )

    def get_active_rooms_managed_by_user(self, user: User) -> list[Room]:
        logger.info(f"Getting active rooms managed by {user}")
        return self.database_repository.get_active_rooms_managed_by_user(user.id)

    def create_user(self, user: User):
        logger.info(f"Creating user {user}")
        self.database_repository.create_user(
            id=user.id,
            username=user.username,
            name=user.name,
        )

    def get_user(self, user: User) -> User:
        logger.info(f"Getting user {user}")
        return self.database_repository.get_user(user.id)

    def leave_room(self, user: User):
        """Make the user leave their current room.

        Raises
            `UserNotFound` if the user does not exist
            `NotInRoom` if the user is not in any room
        """
        logger.info(f"User {user} leaving room id={user}")
        self.database_repository.leave_room(user.id)

    def set_user_name(self, user: User, name: str):
        logger.info(f"Setting user {user} name to {name}")
        self.database_repository.set_user_name(user.id, name)
