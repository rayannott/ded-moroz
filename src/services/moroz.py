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
            MaxNumberOfRoomsReached if the user already manages
                the maximum allowed number of rooms
            UserNotFound if the user does not exist
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
        logger.info(f"Room created: {room}")
        return room

    def join_room(self, user_id: int, room_id: int):
        """Join the user to the given room.

        Raises
            AlreadyInRoom if the user is already in the room
            UserNotFound if the user does not exist
        """
        logger.info(f"User id={user_id} joining room id={room_id}")
        self.database_repository.join_room(
            user_id=user_id,
            room_id=room_id,
        )

    def create_user(self, user: User):
        logger.info(f"Creating user: {user}")
        self.database_repository.create_user(
            id=user.id,
            username=user.username,
            name=user.name,
        )

    def get_user(self, user: User) -> User:
        logger.info(f"Getting user: {user}")
        return self.database_repository.get_user(user.id)

    def leave_room(self, user: User) -> bool:
        logger.info(f"User {user} leaving room id={user}")
        return True

    def set_user_name(self, user: User, name: str) -> bool:
        logger.info(f"Setting user {user} name to {name}")
        return True
