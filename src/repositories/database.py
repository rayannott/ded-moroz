import random

from loguru import logger
from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.models.room import Room
from src.models.target import Target
from src.models.user import User
from src.shared.exceptions import (
    NotInRoom,
    RoomNotFound,
    TargetNotAssigned,
    UserAlreadyExists,
    UserNotFound,
)


class DatabaseRepository:
    def __init__(self, engine: Engine):
        self.engine = engine
        SQLModel.metadata.create_all(engine)
        self.session = sessionmaker(engine)

    def create_room(self, created_by_user_id: int, room_name: str) -> Room:
        logger.debug(f"Creating room {room_name!r} by user id={created_by_user_id}")
        room_id = random.randbytes(4).hex()

        room = Room(
            id=room_id,
            short_code=int(room_id, 16) % 10_000,
            name=room_name,
            manager_user_id=created_by_user_id,
        )

        with self.session() as s:
            s.add(room)
            s.commit()
            s.refresh(room)
            logger.debug(f"Added room {room}")
            return room

    def assign_targets(self, room_id: str, user_target_pairs: list[tuple[int, int]]):
        logger.debug(f"Adding targets in room {room_id=}: {user_target_pairs=}")
        with self.session() as s:
            targets = [
                Target(room_id=room_id, user_id=u_id, target_user_id=t_id)
                for u_id, t_id in user_target_pairs
            ]
            s.add_all(targets)
            s.commit()
            logger.debug(f"Added {len(targets)} targets for {room_id=}")

    def get_target(self, room_id: str, user_id: int) -> User:
        logger.debug(f"Getting target in room {room_id=} for user {user_id=}")
        with self.session() as s:
            target = (
                s.query(Target)
                .filter(
                    Target.room_id == room_id,  # type: ignore[arg-type]
                    Target.user_id == user_id,  # type: ignore[arg-type]
                )
                .first()
            )
        if target is None:
            raise TargetNotAssigned(f"User {user_id=} has no target in room {room_id=}")
        target_user = self.get_user(user_id=target.target_user_id)
        logger.debug(f"Got target {target_user} in room {room_id=} for user {user_id=}")
        return target_user

    def get_room_by_short_code(self, short_code: int) -> Room:
        logger.debug(f"Getting room by {short_code=}")
        with self.session() as s:
            rooms = s.query(Room).filter(Room.short_code == short_code).all()  # type: ignore[arg-type]
        if not rooms:
            raise RoomNotFound(f"Room {short_code=} not found")
        if len(rooms) > 1:
            logger.warning(f"More than one room found with {short_code=}: {rooms}")
            return max(rooms, key=lambda r: r.created_dt)
        logger.debug(f"Get room by {short_code=}: {rooms[0]}")
        return rooms[0]

    def create_user(self, id: int, username: str | None, name: str | None) -> User:
        logger.debug(f"Creating user {id=}, {username=}, {name=}")
        with self.session() as s:
            if s.get(User, id) is not None:
                raise UserAlreadyExists(f"User id={id} already exists")

            user = User(
                id=id,
                username=username,
                name=name,
                joined_dt=DateTime.utcnow(),
            )

            s.add(user)
            s.commit()
            s.refresh(user)
            logger.debug(f"Created user {user}")
            return user

    def get_room(self, room_id: str) -> Room:
        logger.debug(f"Getting room {room_id=}")
        with self.session() as s:
            room = s.get(Room, room_id)
        if room is None:
            raise RoomNotFound(f"Room {room_id=} not found")
        logger.debug(f"Got {room}")
        return room

    def get_user(self, user_id: int) -> User:
        logger.debug(f"Getting user {user_id=}")
        with self.session() as s:
            user = s.get(User, user_id)
        if user is None:
            raise UserNotFound(f"User {user_id=} not found")
        logger.debug(f"Got {user}")
        return user

    def get_rooms_managed_by_user(self, user_id: int) -> list[Room]:
        logger.debug(f"Getting rooms managed by user {user_id=}")
        # raises UserNotFound
        _ = self.get_user(user_id=user_id)  # raises if not found

        with self.session() as s:
            rooms = s.query(Room).filter(Room.manager_user_id == user_id).all()  # type: ignore[arg-type]
        logger.debug(f"Got rooms managed by user {user_id=}: {rooms}")
        return rooms

    def get_active_rooms_managed_by_user(self, user_id: int) -> list[Room]:
        logger.debug(f"Getting active rooms managed by user {user_id=}")
        # raises UserNotFound
        all_rooms = self.get_rooms_managed_by_user(user_id=user_id)
        managed_rooms = [room for room in all_rooms if room.is_active()]
        logger.debug(f"Got active rooms managed by user {user_id=}: {managed_rooms}")
        return managed_rooms

    def get_users_in_room(self, room_id: str) -> list[User]:
        logger.debug(f"Getting users in room {room_id=}")
        # raises RoomNotFound
        _ = self.get_room(room_id=room_id)  # raises if not found

        with self.session() as s:
            users = s.query(User).filter(User.room_id == room_id).all()  # type: ignore[arg-type]
        logger.debug(f"Got users in room {room_id=}: {users}")
        return users

    def join_room(self, user_id: int, room_id: str):
        logger.debug(f"User {user_id=} joining {room_id=}")
        # raises UserNotFound, RoomNotFound
        with self.session() as s:
            user = s.get(User, user_id)
            if user is None:
                raise UserNotFound(f"User with id={user_id} not found")
            room = s.get(Room, room_id)
            if room is None:
                raise RoomNotFound(f"Room with {room_id=} not found")
            user.room_id = room_id
            s.commit()
            logger.debug(f"User {user} joined {room}")

    def delete_room(self, room_id: str):
        logger.debug(f"Deleting {room_id=}")
        # raises RoomNotFound
        with self.session() as s:
            room = s.get(Room, room_id)
            if room is None:
                raise RoomNotFound(f"Room with {room_id=} not found")
            s.delete(room)
            s.commit()
            logger.debug(f"Deleted {room}")

    def leave_room(self, user_id: int) -> Room:
        logger.debug(f"User id={user_id} leaving room")
        # raises UserNotFound, NotInRoom
        with self.session() as s:
            user = s.get(User, user_id)
            if user is None:
                raise UserNotFound(f"User with id={user_id} not found")
            if (room_id := user.room_id) is None:
                raise NotInRoom(f"User id={user_id} is not in any room")
            room = self.get_room(room_id)
            user.room_id = None
            s.commit()
            logger.debug(f"User {user_id=} left {room_id=}")
            return room

    def set_user_name(self, user_id: int, name: str):
        logger.debug(f"Setting user {user_id=} {name=}")
        # raises UserNotFound
        with self.session() as s:
            user = s.get(User, user_id)
            if user is None:
                raise UserNotFound(f"User with id={user_id} not found")
            user.name = name
            s.commit()
            logger.debug(f"Set {user_id=} {name=}")

    def set_game_started(self, room_id: str, started_dt: DateTime):
        logger.debug(f"Setting game started dt for room {room_id=} to {started_dt=}")
        # raises RoomNotFound
        with self.session() as s:
            room = s.get(Room, room_id)
            if room is None:
                raise RoomNotFound(f"Room with {room_id=} not found")
            room.started_dt = started_dt
            s.commit()
            logger.debug(f"Set game started dt for room {room_id=} to {started_dt=}")

    def set_game_completed(self, room_id: str, completed_dt: DateTime):
        logger.debug(
            f"Setting game completed_dt for room {room_id=} to {completed_dt=}"
        )
        # raises RoomNotFound
        with self.session() as s:
            room = s.get(Room, room_id)
            if room is None:
                raise RoomNotFound(f"Room with {room_id=} not found")
            room.completed_dt = completed_dt
            s.commit()
            logger.debug(
                f"Set game completed_dt for room {room_id=} to {completed_dt=}"
            )
