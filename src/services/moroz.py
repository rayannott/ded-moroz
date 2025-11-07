from loguru import logger

from src.models.room import Room
from src.repositories.database import DatabaseRepository
from src.settings import Settings
from src.shared.exceptions import MaxNumberOfRoomsReached, AlreadyInRoom, UserNotFound


class DedMoroz:
    """The main game logic."""

    def __init__(
        self,
        database_repository: DatabaseRepository,
        settings: Settings,
    ):
        self.database_repository = database_repository
        self.settings = settings

    def create_room(self, created_by_user_id: int, room_name: str) -> Room:
        """Create a new room managed by the given user
        and return it.

        Raises
            MaxNumberOfRoomsReached if the user already manages
                the maximum allowed number of rooms
            UserNotFound if the user does not exist
        """
        logger.debug(f"Creating room {room_name!r} by user id={created_by_user_id}")
        managed_rooms = self.database_repository.get_rooms_managed_by_user(
            user_id=created_by_user_id
        )
        active_managed_rooms = [room for room in managed_rooms if room.is_active()]
        if len(active_managed_rooms) >= self.settings.max_rooms_managed_by_user:
            raise MaxNumberOfRoomsReached(
                f"User {created_by_user_id} already manages "
                f"{len(active_managed_rooms)} rooms, "
                f"the maximum allowed number is "
                f"{self.settings.max_rooms_managed_by_user}"
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
        logger.debug(f"User id={user_id} joining room id={room_id}")
        self.database_repository.join_room(
            user_id=user_id,
            room_id=room_id,
        )

    def leave_room(self, user_id: int, room_id: int) -> bool:
        return True

    def set_user_name(self, user_id: int, name: str) -> bool:
        return True
