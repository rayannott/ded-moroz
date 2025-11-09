import random
from itertools import pairwise

from loguru import logger
from pydantic_extra_types.pendulum_dt import DateTime

from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from src.shared.exceptions import (
    AlreadyInRoom,
    MaxNumberOfRoomsReached,
    NotInRoom,
    RoomTooSmall,
    UserNotFound,
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

    def delete_room(self, room_id: str) -> list[User]:
        """Delete the given room if the user is its manager.

        Raises
            `RoomNotFound` if the room does not exist
        """
        logger.info(f"Deleting room id={room_id} by its manager")
        users_in_room = self.database_repository.get_users_in_room(room_id)
        for user in users_in_room:
            try:
                self.leave_room(user)
            except (UserNotFound, NotInRoom):
                logger.opt(exception=True).critical(
                    f"Error removing user {user} from deleted room id={room_id}"
                )
            logger.info(f"User {user} removed from deleted room id={room_id}")
        self.database_repository.delete_room(
            room_id=room_id,
        )
        logger.info(f"Room deleted: {room_id}")
        return users_in_room

    def join_room_by_short_code(self, user: User, room_short_code: int) -> Room:
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
        return room

    def start_game_in_room(self, room: Room) -> list[tuple[User, User]]:
        logger.info(f"Starting game in room {room}")
        users_in_room = self.database_repository.get_users_in_room(room.id)
        if len(users_in_room) < 2:
            raise RoomTooSmall(
                f"Cannot start game in room {room.id=} with "
                f"only {len(users_in_room)} users; minimum is 2"
            )
        logger.info(f"Game started in room {room} with users {users_in_room}")
        random.shuffle(users_in_room)
        target_pairs: list[tuple[User, User]] = [
            (user, target)
            for user, target in pairwise(users_in_room + [users_in_room[0]])
        ]
        for user, target in target_pairs:
            self.database_repository.add_target(
                room_id=room.id,
                user_id=user.id,
                target_user_id=target.id,
            )
        self.database_repository.set_game_completed(
            room_id=room.id,
            started_dt=DateTime.utcnow(),
        )
        return target_pairs

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
