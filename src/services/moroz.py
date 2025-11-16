import random
from dataclasses import dataclass
from itertools import pairwise

from loguru import logger
from pydantic_extra_types.pendulum_dt import DateTime

from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from src.shared.exceptions import (
    AlreadyInRoom,
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

    def create_room(self, created_by_user_id: int, room_name: str) -> Room:
        """Create a new room managed by the given user
        and return it.

        Raises
            `MaxNumberOfRoomsReached` if the user already manages
                the maximum allowed number of rooms
            `UserNotFound` if the user does not exist
        """
        logger.info(f"Creating room {room_name!r} by {created_by_user_id=}")
        active_managed_rooms = (
            self.database_repository.get_active_rooms_managed_by_user(
                user_id=created_by_user_id
            )
        )
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
            room_name=room_name,
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
            self.leave_room(user)
        self.database_repository.delete_room(
            room_id=room_id,
        )
        logger.success(f"Room deleted {room_id=}")
        return users_in_room

    def join_room_by_short_code(self, user: User, room_short_code: int) -> Room:
        """Join the user to the given room.

        Raises
            `RoomNotFound` if the room does not exist
            `AlreadyInRoom` if the user is already in some room
            `UserNotFound` if the user does not exist
            `GameAlreadyStarted` if the game in the room has already started
            `GameAlreadyCompleted` if the game in the room has already completed
        """
        logger.info(f"User {user} joining {room_short_code=}")
        user = self.database_repository.get_user(user.id)
        if user.room_id is not None:
            msg = f"User {user.id=} is already in room id={user.room_id}"
            logger.info(msg)
            raise AlreadyInRoom(msg)
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

    def start_game_in_room(self, room: Room) -> list[tuple[User, User]]:
        logger.info(f"Starting game in room {room}")
        users_in_room = self.database_repository.get_users_in_room(room.id)
        if len(users_in_room) < self.min_players_to_start_game:
            msg = (
                f"Cannot start game in room {room.id=} with "
                f"only {len(users_in_room)} users; minimum is {self.min_players_to_start_game}"
            )
            logger.info(msg)
            raise RoomTooSmall(msg)
        logger.info(f"Game started in {room} with users {users_in_room}")
        random.shuffle(users_in_room)
        target_pairs: list[tuple[User, User]] = [
            (user, target)
            for user, target in pairwise(users_in_room + [users_in_room[0]])
        ]
        self.database_repository.assign_targets(
            room_id=room.id,
            user_target_pairs=[(user.id, target.id) for user, target in target_pairs],
        )
        self.database_repository.set_game_started(
            room_id=room.id,
            started_dt=DateTime.utcnow(),
        )
        logger.success(f"Game started in room {room}")
        return target_pairs

    def complete_game_in_room(self, room: Room) -> list[User]:
        logger.info(f"Completing game in room {room}")
        users_in_room = self.database_repository.get_users_in_room(room.id)
        self.database_repository.set_game_completed(
            room_id=room.id,
            completed_dt=DateTime.utcnow(),
        )
        for usr in users_in_room:
            self.leave_room(user=usr)
        logger.success(f"Game completed in room {room}")
        return users_in_room

    def get_active_rooms_managed_by_user(self, user: User) -> list[Room]:
        logger.info(f"Getting active rooms managed by {user}")
        return self.database_repository.get_active_rooms_managed_by_user(user.id)

    def create_user(self, user: User) -> User:
        logger.info(f"Creating {user}")
        new_user = self.database_repository.create_user(
            id=user.id,
            username=user.username,
            name=user.name,
        )
        logger.success(f"Created {new_user}")
        return new_user

    def get_room_information(self, room: Room) -> str:
        logger.info(f"Getting information about {room}")
        this_room = self.database_repository.get_room(room.id)
        msg = f"Room {this_room.display_short_code} ({this_room.name})\n"
        manager = self.database_repository.get_user(this_room.manager_user_id)
        msg += f"Managed by {manager.formal_display_name}"
        msg += f"\nCreated at {this_room.created_dt}"
        users_in_room = self.database_repository.get_users_in_room(this_room.id)
        msg += "\nParticipants:\n  "
        msg += (
            "\n".join(usr.formal_display_name for usr in users_in_room)
            or "No participants yet"
        )
        if this_room.game_started:
            msg += f"\nGame started at {this_room.started_dt}"
            if this_room.game_completed:
                msg += f"\nGame completed at {this_room.completed_dt}"
            else:
                msg += "\nGame is ongoing..."
        else:
            msg += "\nGame has not started yet"
        logger.success(f"Got information about {this_room}.")
        return msg

    def get_user_information(self, user: User) -> str:
        logger.info(f"Getting information about {user}")
        this_user = self.database_repository.get_user(user.id)
        msg = f"You are {this_user.display_name}"
        if this_user.username is not None:
            msg += f" (@{this_user.username})"
        if this_user.room_id is None:
            logger.success(f"Got information about {this_user} (not in any room).")
            return msg + "\nnot in any room."
        room = self.database_repository.get_room(this_user.room_id)
        msg += (
            f"\ncurrently in room {room.display_short_code} (created {room.created_dt})"
        )
        that_room_manager = self.database_repository.get_user(room.manager_user_id)
        msg += f" managed by {that_room_manager.display_name}"
        # TODO show number of participants
        try:
            target = self.database_repository.get_target(
                this_user.room_id, this_user.id
            )
            started_at = (
                room.started_dt if room.started_dt is not None else "unknown time"
            )
            if started_at == "unknown time":
                logger.error(f"Game in room {room} has started but started_dt is None")
            msg += f"\nYour target is {target.display_name} (assigned when game started at {started_at})"
        except TargetNotAssigned:
            msg += "\nGame has not started yet; no target assigned"
        logger.success(f"Got information about {this_user}.")
        return msg

    def update_name(self, user: User, name: str):
        logger.info(f"Updating {user} name to {name}")
        status = is_name_valid(name)
        if not status:
            logger.info(f"Invalid name {name!r} provided by {user}: {status.reason}")
            raise InvalidName(status.reason)
        self.database_repository.set_user_name(user.id, name)
        logger.success(f"Updated {user} name to {name}")

    def get_user(self, user: User) -> User:
        logger.info(f"Getting {user}")
        return self.database_repository.get_user(user.id)

    def get_room(self, room_id: str) -> Room:
        logger.info(f"Getting {room_id=}")
        return self.database_repository.get_room(room_id)

    def leave_room(self, user: User) -> Room:
        """Make the user leave their current room.

        Raises
            `UserNotFound` if the user does not exist
            `NotInRoom` if the user is not in any room
        """
        logger.info(f"User {user} leaving room id={user}")
        left_room = self.database_repository.leave_room(user.id)
        logger.success(f"User {user} left their room")
        return left_room

    def set_locale(self, user_id: int, locale_code: str):
        logger.info(f"Setting locale for user {user_id=} to {locale_code=}")
        self.database_repository.set_locale(user_id, locale_code)
        logger.success(f"Set locale for user {user_id=} to {locale_code=}")
