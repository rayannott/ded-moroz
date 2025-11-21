import random
from dataclasses import dataclass
from itertools import pairwise

from loguru import logger
from pydantic_extra_types.pendulum_dt import DateTime

from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from src.shared.exceptions import (
    GameAlreadyCompleted,
    GameAlreadyStarted,
    InvalidName,
    MaxNumberOfRoomsReached,
    RoomTooSmall,
    TargetNotAssigned,
)
from src.shared.utils import is_name_valid


@dataclass
class Moroz:
    """The main game logic."""

    database_repository: DatabaseRepository
    max_rooms_managed_by_user: int
    min_players_to_start_game: int
    admin_name: str | None = None
    admin_username: str | None = None
    admin_user_id: int | None = None

    def create_room(self, created_by_user_id: int) -> Room:
        """Create a new room managed by the given user
        and return it.

        Raises
            `MaxNumberOfRoomsReached` if the user already manages
                the maximum allowed number of rooms
            `UserNotFound` if the user does not exist
        """
        logger.info(f"Creating room by {created_by_user_id=}")
        managed_rooms = self.database_repository.get_rooms_managed_by_user(
            user_id=created_by_user_id
        )
        active_managed_rooms = [room for room in managed_rooms if room.is_active]
        if len(active_managed_rooms) >= self.max_rooms_managed_by_user:
            msg = (
                "Maximum number of rooms reached: "
                f"user {created_by_user_id=} already manages "
                f"{len(active_managed_rooms)} rooms, "
                f"the maximum allowed number is "
                f"{self.max_rooms_managed_by_user}"
            )
            logger.info(msg)
            raise MaxNumberOfRoomsReached(msg)
        room = self.database_repository.create_room(
            created_by_user_id=created_by_user_id,
        )
        logger.success(f"Room created {room=}")
        return room

    def delete_room(self, room_id: str) -> list[User]:
        """Delete the given room if the user is its manager.

        Raises
            `RoomNotFound` if the room does not exist
        """
        logger.info(f"Deleting {room_id=} by its manager")
        users_in_room = self.database_repository.get_users_in_room(room_id)
        for user in users_in_room:
            self.leave_room(user_id=user.id)
        self.database_repository.delete_room(
            room_id=room_id,
        )
        logger.success(f"Room deleted {room_id=}")
        return users_in_room

    def join_room_by_short_code(self, user_id: int, room_short_code: int) -> Room:
        """Join the user to the given room.

        Raises
            `RoomNotFound` if the room does not exist
            `UserNotFound` if the user does not exist
            `GameAlreadyStarted` if the game in the room has already started
            `GameAlreadyCompleted` if the game in the room has already completed
        """
        logger.info(f"User {user_id} joining {room_short_code=}")
        user = self.database_repository.get_user(user_id)
        room = self.database_repository.get_room_by_short_code(room_short_code)
        if room.game_started:
            msg = f"Game in room {room.id} has already started"
            logger.info(msg)
            raise GameAlreadyStarted(msg)
        if room.game_completed:
            msg = f"Game in room {room.id} has already completed"
            logger.info(msg)
            raise GameAlreadyCompleted(msg)
        self.database_repository.join_room(
            user_id=user.id,
            room_id=room.id,
        )
        logger.success(f"User {user} joined {room}")
        return room

    def start_game_in_room(self, room_id: str) -> list[tuple[User, User]]:
        logger.info(f"Starting game in {room_id=}")
        users_in_room = self.database_repository.get_users_in_room(room_id)
        if len(users_in_room) < self.min_players_to_start_game:
            msg = (
                f"Cannot start game in {room_id=} with "
                f"only {len(users_in_room)} users; minimum is {self.min_players_to_start_game}"
            )
            logger.info(msg)
            raise RoomTooSmall(msg)
        logger.info(f"Game started in {room_id=} with users {users_in_room}")
        random.shuffle(users_in_room)
        target_pairs: list[tuple[User, User]] = [
            (user, target)
            for user, target in pairwise(users_in_room + [users_in_room[0]])
        ]
        self.database_repository.assign_targets(
            room_id=room_id,
            user_target_pairs=[(user.id, target.id) for user, target in target_pairs],
        )
        self.database_repository.set_game_started(
            room_id=room_id,
            started_dt=DateTime.utcnow(),
        )
        logger.success(f"Game started in {room_id=}")
        return target_pairs

    def complete_game_in_room(self, room_id: str) -> list[User]:
        logger.info(f"Completing game in room {room_id=}")
        users_in_room = self.database_repository.get_users_in_room(room_id)
        self.database_repository.set_game_completed(
            room_id=room_id,
            completed_dt=DateTime.utcnow(),
        )
        for usr in users_in_room:
            self.leave_room(user_id=usr.id)
        logger.success(f"Game completed in {room_id=}")
        return users_in_room

    def get_rooms_managed_by_user(self, user_id: int) -> list[Room]:
        logger.info(f"Getting rooms managed by {user_id=}")
        return self.database_repository.get_rooms_managed_by_user(user_id)

    def create_user(self, user_id: int, username: str | None, name: str | None) -> User:
        logger.info(
            f"Creating user with id={user_id}, username={username}, name={name}"
        )
        new_user = self.database_repository.create_user(
            id=user_id, username=username, name=name
        )
        logger.success(f"Created {new_user}")
        return new_user

    def get_room_information(self, room_id: str) -> str:
        logger.info(f"Getting information about {room_id=}")

        room = self.database_repository.get_room(room_id)
        manager = self.database_repository.get_user(room.manager_user_id)
        participants = self.database_repository.get_users_in_room(room.id)

        lines: list[str] = []

        lines.append(f"Room {room.display_short_code}")
        lines.append(f"  managed by: {manager.formal_display_name}")
        lines.append(f"  created at: {room.created_dt}")

        if participants:
            lines.append("  participants:")
            for usr in participants:
                lines.append(f"    {usr.formal_display_name}")
        else:
            lines.append("  participants: none")

        if not room.game_started:
            lines.append("  game status: not started yet.")
        else:
            lines.append(f"  game status: started at {room.started_dt}")
            if room.game_completed:
                lines.append(f"  completed at: {room.completed_dt}")

        msg = "\n".join(lines)
        logger.success(f"Got information about {room=}")
        return msg

    def get_user_information(self, user_id: int) -> str:
        logger.info(f"Getting information about {user_id=}")

        user = self.database_repository.get_user(user_id)

        lines: list[str] = []
        lines.append(f"You are {user.formal_display_name}!")

        if rooms_managed_by_user := self.database_repository.get_rooms_managed_by_user(
            user.id
        ):
            active_managed_rooms = [
                room for room in rooms_managed_by_user if room.is_active
            ]
            lines.append("")
            lines.append(
                f"Active rooms you manage: {', '.join(room.display_short_code for room in active_managed_rooms)}"
            )

        lines.append("")
        if user.room_id is None:
            lines.append("Status: not in any room.")
            msg = "\n".join(lines)
            logger.success(f"Got information about {user=} (not in any room)")
            return msg

        room = self.database_repository.get_room(user.room_id)

        lines.append("You are in " + self.get_room_information(room.id))

        # if the game has started, show the target
        try:
            target_user = self.database_repository.get_target(room.id, user.id)
            lines.append(f"Your target is: {target_user.formal_display_name} 🎁")
        except TargetNotAssigned:
            pass

        msg = "\n".join(lines)
        logger.success(f"Got information about {user=}")
        return msg

    def update_name(self, user_id: int, name: str):
        logger.info(f"Updating {user_id=} name to {name=}")
        status = is_name_valid(name)
        if not status:
            logger.info(
                f"Invalid name {name!r} provided by {user_id=}: {status.reason}"
            )
            raise InvalidName(status.reason)
        self.database_repository.set_user_name(user_id, name)
        logger.success(f"Updated {user_id=} name to {name=}")

    def get_user(self, user_id: int) -> User:
        logger.info(f"Getting {user_id=}")
        return self.database_repository.get_user(user_id)

    def get_users_in_room(self, room_id: str) -> list[User]:
        logger.info(f"Getting users in room id={room_id}")
        return self.database_repository.get_users_in_room(room_id)

    def get_room(self, room_id: str) -> Room:
        logger.info(f"Getting {room_id=}")
        return self.database_repository.get_room(room_id)

    def leave_room(self, user_id: int) -> Room:
        """Make the user leave their current room.

        Raises
            `UserNotFound` if the user does not exist
            `NotInRoom` if the user is not in any room
        """
        logger.info(f"User {user_id} leaving room id={user_id}")
        left_room = self.database_repository.leave_room(user_id)
        logger.success(f"User {user_id} left their room")
        return left_room
