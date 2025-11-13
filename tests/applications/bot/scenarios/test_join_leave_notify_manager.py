from unittest import mock

import pytest

# Assuming the location of JoinCallback based on your project structure
from src.applications.bot.callbacks.join import JoinCallback
from src.applications.bot.callbacks.leave import LeaveCallback
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestJoinLeaveNotifyManager:
    """Getting notifications when someone joins/leaves the room.

    Given:
    - two users: u1 and u2
    - a room created by u1
    When:
    - u2 joins the room
    Then:
    - u1 receives a notification about u2 joining
    When:
    - u2 leaves the room
    Then:
    - u1 receives a notification about u2 leaving
    """

    @pytest.fixture
    def join_callback(self, bot_mock, moroz_integrated) -> JoinCallback:
        return JoinCallback(bot=bot_mock, moroz=moroz_integrated)

    @pytest.fixture
    def leave_callback(self, bot_mock, moroz_integrated) -> LeaveCallback:
        return LeaveCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_join_leave_notify_manager(
        self,
        join_callback: JoinCallback,
        leave_callback: LeaveCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        manager = database_repo.create_user(id=201, username="manager", name="Manager")
        joiner = database_repo.create_user(id=202, username="joiner", name="Joiner")

        room = database_repo.create_room(
            created_by_user_id=manager.id,
            room_name="Test Room",
        )

        message = message_factory(text="/join", chat_id=joiner.id)

        # WHEN
        joiner_user = database_repo.get_user(joiner.id)
        join_callback.process(message, joiner_user)

        # THEN
        _, (_answer, callback_fn), _kwargs = (
            bot_mock.register_next_step_handler.mock_calls[0]
        )
        assert callback_fn == join_callback._handle_room_code_entered

        # WHEN (user enters room code)
        answer_message = message_factory(
            text=room.display_short_code, chat_id=joiner.id
        )
        callback_fn(answer_message, user=joiner_user)

        # THEN
        users_in_room = database_repo.get_users_in_room(room.id)
        assert len(users_in_room) == 1
        assert users_in_room[0].id == joiner.id
        assert bot_mock.send_message.call_count == 3

        # WHEN (the joiner leaves the room)
        leave_message = message_factory(text="/leave", chat_id=joiner.id)
        leave_callback.process(leave_message, joiner_user)

        # THEN
        users_in_room = database_repo.get_users_in_room(room.id)
        assert len(users_in_room) == 0

        calls = [
            mock.call(joiner.id, Regex("Please enter.+")),
            mock.call(joiner.id, Regex("You have successfully joined the room.+")),
            mock.call(manager.id, Regex("User Joiner.+has joined your room.+")),
            mock.call(joiner.id, Regex("You have successfully left the room.+")),
            mock.call(manager.id, Regex("User Joiner.+has left your room.+")),
        ]

        bot_mock.send_message.assert_has_calls(calls)
        assert bot_mock.send_message.call_count == 5
