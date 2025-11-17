import re
from unittest import mock

import pytest
from pydantic_extra_types.pendulum_dt import DateTime

from src.applications.bot.callbacks.management.info import InfoCallback
from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestGetRoomInformation:
    @pytest.fixture
    def info_callback(self, bot_mock, moroz_integrated) -> InfoCallback:
        return InfoCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_empty_room(
        self,
        info_callback: InfoCallback,
        bot_mock,
        create_manager_room: tuple[User, Room],
    ):
        # GIVEN
        manager, room = create_manager_room

        # WHEN
        info_callback.process_management(manager, room)

        # assert: bot was called once with the correct user and message
        bot_mock.send_message.assert_called_once_with(
            manager.id,
            Regex(
                r"Room.+participants: none.+game status: not started yet\.",
                flags=re.DOTALL,
            ),
            reply_markup=mock.ANY,
        )

    def test_room_with_participants_not_started(
        self,
        info_callback: InfoCallback,
        database_repo: DatabaseRepository,
        bot_mock,
        create_manager_room: tuple[User, Room],
    ):
        # GIVEN
        manager, room = create_manager_room
        participant1 = database_repo.create_user(
            id=302, username="participant1", name="P1"
        )
        participant2 = database_repo.create_user(
            id=303, username="participant2", name="P2"
        )
        database_repo.join_room(user_id=participant1.id, room_id=room.id)
        database_repo.join_room(user_id=participant2.id, room_id=room.id)

        # WHEN
        info_callback.process_management(manager, room)

        # THEN
        bot_mock.send_message.assert_called_once_with(
            manager.id,
            Regex(
                r"Room.+participants:.+P1.+P2.+game status: not started yet\.",
                flags=re.DOTALL,
            ),
            reply_markup=mock.ANY,
        )

    def test_room_with_participants_started(
        self,
        info_callback: InfoCallback,
        database_repo: DatabaseRepository,
        bot_mock,
        create_manager_room: tuple[User, Room],
    ):
        # GIVEN
        manager, room = create_manager_room
        participant1 = database_repo.create_user(
            id=304, username="participant1", name="P1"
        )
        database_repo.join_room(user_id=participant1.id, room_id=room.id)
        database_repo.set_game_started(room.id, started_dt=DateTime.utcnow())
        manager = database_repo.get_user(manager.id)
        room = database_repo.get_room(room.id)

        # WHEN
        info_callback.process_management(manager, room)

        # THEN
        bot_mock.send_message.assert_called_once_with(
            manager.id,
            Regex(
                r"Room.+participants:.+P1.+game status: started at.+",
                flags=re.DOTALL,
            ),
            reply_markup=mock.ANY,
        )

    def test_room_with_participants_completed(
        self,
        info_callback: InfoCallback,
        database_repo: DatabaseRepository,
        bot_mock,
        create_manager_room: tuple[User, Room],
    ):
        # GIVEN
        manager, room = create_manager_room
        participant1 = database_repo.create_user(
            id=305, username="participant1", name="P1"
        )
        database_repo.join_room(user_id=participant1.id, room_id=room.id)
        database_repo.set_game_started(room.id, started_dt=DateTime.utcnow())
        database_repo.set_game_completed(room.id, completed_dt=DateTime.utcnow())
        manager = database_repo.get_user(manager.id)
        room = database_repo.get_room(room.id)

        # WHEN
        info_callback.process_management(manager, room)

        # THEN
        bot_mock.send_message.assert_called_once_with(
            manager.id,
            Regex(
                r"Room.+participants:.+P1.+game status: started at.+completed at.+",
                flags=re.DOTALL,
            ),
            reply_markup=mock.ANY,
        )
