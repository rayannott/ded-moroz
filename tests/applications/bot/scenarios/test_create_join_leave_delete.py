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


class TestCreateJoinLeaveDelete:
    """Test the full scenario of creating, joining, and leaving a room.

    Given:
        - a registered user
    When (create):
        - the user creates a room
    Then:
        - the room is created successfully
    When (join):
        - the user joins the created room
    Then:
        - the user joins the room successfully
    When (leave):
        - the user leaves the room
    Then:
        - the user leaves the room successfully
    When (delete):
        - the user deletes the room
    Then:
        - the room is deleted successfully
    ...
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
        managed_rooms_init = database_repo.get_rooms_managed_by_user(user_mock.id)

        # WHEN Create
        create_callback.process(user_mock, message=create_message)

        # THEN Create
        managed_rooms = database_repo.get_rooms_managed_by_user(user_mock.id)
        assert len(managed_rooms_init) == 0
        assert len(managed_rooms) == 1
        created_room: Room = managed_rooms[0]
        bot_mock.send_message.assert_called_once_with(
            user_mock.id,
            Regex(r"Room created.+ID: `\d{4}`.+", flags=re.DOTALL),
            parse_mode="MarkdownV2",
        )
        assert "Room created" in caplog.text

        # WHEN Join (initiated)
        join_message = message_factory(text="/join")
        this_user = database_repo.get_user(user_mock.id)
        join_callback.process(this_user, message=join_message)

        # THEN Join
        _, (_answer, callback_fn), _kwargs = (
            bot_mock.register_next_step_handler.mock_calls[0]
        )
        initiated_join_call = mock.call(
            user_mock.id,
            Regex("Please enter.+"),
        )
        assert callback_fn == join_callback._handle_room_code_entered

        # WHEN Join (room code entered)
        answer_message = message_factory(text=created_room.display_short_code)
        callback_fn(answer_message, user=this_user)

        # THEN Join
        assert "joining room with code" in caplog.text
        successful_join_call = mock.call(
            this_user.id,
            Regex(".+successfully joined the room.+"),
        )
        successful_join_call_manager = mock.call(
            this_user.id,
            Regex("User .+ has joined your room.+"),
        )

        # WHEN Leave
        leave_message = message_factory(text="/leave")
        this_user = database_repo.get_user(user_mock.id)
        leave_callback.process(this_user, message=leave_message)

        # THEN Leave
        successful_leave_call = mock.call(
            this_user.id,
            Regex(".+successfully left the room.+"),
        )
        successful_leave_call_manager = mock.call(
            this_user.id,
            Regex("User .+ has left your room.+"),
        )

        bot_mock.send_message.assert_has_calls(
            [
                initiated_join_call,
                successful_join_call,
                successful_join_call_manager,
                successful_leave_call,
                successful_leave_call_manager,
            ]
        )
