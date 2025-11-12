import re
from unittest import mock

import pytest
from pytest import LogCaptureFixture
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.create import CreateCallback
from src.applications.bot.callbacks.join import JoinCallback
from src.applications.bot.callbacks.leave import LeaveCallback
from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestCreateJoinLeave:
    """Test the full scenario of creating, joining, and leaving a room.

    Given:
    - a registered user
    When:
    - the user creates a room
    - the user joins the created room
    - the user leaves the room
    Then:
    - the room is created successfully
    - the user joins the room successfully
    - the user leaves the room successfully
    - the user receives appropriate messages at each step
    - the user receives notification upon leaving the room (since they are the manager)
    """

    @pytest.fixture
    def create_callback(self, bot_mock, moroz_integrated) -> CreateCallback:
        return CreateCallback(bot=bot_mock, moroz=moroz_integrated)

    @pytest.fixture
    def join_callback(self, bot_mock, moroz_integrated) -> JoinCallback:
        return JoinCallback(bot=bot_mock, moroz=moroz_integrated)

    @pytest.fixture
    def leave_callback(self, bot_mock, moroz_integrated) -> LeaveCallback:
        return LeaveCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_create_join_leave(
        self,
        create_callback: CreateCallback,
        join_callback: JoinCallback,
        leave_callback: LeaveCallback,
        message_factory,
        user_mock: User,
        database_repo: DatabaseRepository,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        database_repo.create_user(user_mock.id, user_mock.username, user_mock.name)
        create_message = message_factory(text="/create")
        managed_rooms_init = database_repo.get_active_rooms_managed_by_user(
            user_mock.id
        )

        # WHEN Create
        create_callback.process(create_message, user_mock)

        # THEN Create
        managed_rooms = database_repo.get_active_rooms_managed_by_user(user_mock.id)
        assert len(managed_rooms_init) == 0
        assert len(managed_rooms) == 1
        created_room: Room = managed_rooms[0]
        bot_mock.send_message.assert_called_with(
            create_message.chat.id,
            Regex(r"Room created.+ID: `\d{4}`.+", flags=re.DOTALL),
            parse_mode="MarkdownV2",
        )
        assert "Room created" in caplog.text

        # TODO complete (how to test the next step methods?)
        # # WHEN Join
        # join_message = message_factory(text="/join")
        # join_callback.process(join_message, user_mock)

        # # Simulate entering room code
        # room_code_message = message_factory(
        #     text=f"{created_room.short_code:04d}",
        #     chat_id=join_message.chat.id,
        #     from_user_id=join_message.from_user.id,
        # )
        # join_callback._handle_room_code_entered(room_code_message, user_mock)

        # # THEN Join
        # updated_user = database_repo.get_user(user_mock.id)
        # assert updated_user.room_id == created_room.id
        # bot_mock.send_message.assert_called_with(
        #     room_code_message.chat.id,
        #     Regex(r"You have successfully joined the room.+"),
        # )
        # assert f"User {user_mock} joining room with code" in caplog.text

        # # WHEN Leave
        # leave_message = message_factory(text="/leave")
        # leave_callback.process(leave_message, user_mock)

        # # THEN Leave
        # updated_user_after_leave = database_repo.get_user(user_mock.id)
        # assert updated_user_after_leave.room_id is None
        # bot_mock.send_message.assert_called_with(
        #     leave_message.chat.id,
        #     "You have successfully left the room! 🎉",
        # )
        # assert f"/leave from {user_mock}" in caplog.text
