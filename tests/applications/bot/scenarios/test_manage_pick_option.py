from unittest import mock

import pytest
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.management.manage import (
    _CANCEL_ACTION,
    ManageCallback,
)
from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestManagePickOption:
    """Manager manages the room."""

    # TODO(test): given the state of the room,
    # the manager should have a certain set of options to pick from
    @pytest.fixture
    def manage_callback(self, bot_mock, moroz_integrated) -> ManageCallback:
        return ManageCallback(bot=bot_mock, moroz=moroz_integrated)

    @pytest.fixture
    def create_user_room(self, database_repo: DatabaseRepository, user_mock: User):
        created_user = database_repo.create_user(
            user_mock.id, user_mock.username, user_mock.name
        )
        created_room = database_repo.create_room(
            created_by_user_id=created_user.id,
            room_name="Test Room",
        )
        this_user = database_repo.get_user(created_user.id)
        return this_user, created_room

    @pytest.fixture
    def get_keyboard_patch(self):
        with mock.patch(
            "src.applications.bot.callbacks.management.manage.get_keyboard"
        ) as get_keyboard_mock:
            yield get_keyboard_mock

    def test_manage_non_manager_tries_to_manage(
        self,
        manage_callback: ManageCallback,
        database_repo: DatabaseRepository,
        message_factory,
        bot_mock,
        create_user_room,
    ):
        # GIVEN
        manager_user, created_room = create_user_room
        message = message_factory(text="/manage")
        some_other_user = database_repo.create_user(
            id=123, username="otheruser", name="Other"
        )
        # WHEN
        manage_callback.process(some_other_user, message=message)
        # THEN
        bot_mock.send_message.assert_called_once_with(
            some_other_user.id,
            Regex("You are not managing.+"),
        )

    def test_manage_manager_initiates_manage_has_room(
        self,
        manage_callback: ManageCallback,
        message_factory,
        create_user_room: tuple[User, Room],
        get_keyboard_patch,
        bot_mock,
    ):
        # GIVEN
        manager_user, created_room = create_user_room
        message = message_factory(text="/manage")
        # WHEN
        manage_callback.process(manager_user, message=message)
        # THEN
        bot_mock.send_message.assert_called_once_with(
            manager_user.id,
            "Please select a room to manage:",
            reply_markup=mock.ANY,
        )
        get_keyboard_patch.assert_called_once_with(
            [created_room.display_short_code, _CANCEL_ACTION]
        )

    def test_manage_manager_cancels(
        self,
        manage_callback: ManageCallback,
        message_factory,
        create_user_room: tuple[User, Room],
        bot_mock,
    ):
        # GIVEN
        manager_user, created_room = create_user_room
        message = message_factory(text="/manage")
        # WHEN
        manage_callback.process(manager_user, message=message)
        _, (_answer, callback_fn), _kwargs = (
            bot_mock.register_next_step_handler.mock_calls[0]
        )
        answer_message = message_factory(text=_CANCEL_ACTION)
        callback_fn(
            answer_message,
            user=manager_user,
            code_to_room={created_room.short_code: created_room},
        )
        # THEN
        bot_mock.send_message.assert_called_with(
            manager_user.id,
            "Room management cancelled.",
            reply_markup=mock.ANY,
        )

    def test_manage_manager_picks_room_to_manage_internal_error(
        self,
        manage_callback: ManageCallback,
        message_factory,
        create_user_room: tuple[User, Room],
        caplog: pytest.LogCaptureFixture,  # noqa: F811
        bot_mock,
    ):
        # GIVEN
        manager_user, created_room = create_user_room
        message = message_factory(text="/manage")
        # WHEN
        manage_callback.process(manager_user, message=message)
        _, (_answer, callback_fn), _kwargs = (
            bot_mock.register_next_step_handler.mock_calls[0]
        )
        answer_message = message_factory(text=created_room.display_short_code)
        callback_fn(
            answer_message,
            user=manager_user,
            code_to_room={},  # empty dict to trigger internal error
        )
        # THEN
        bot_mock.send_message.assert_called_with(
            manager_user.id,
            "Internal error.",
            reply_markup=mock.ANY,
        )
        assert (
            f"Room room_short_code={created_room.short_code} not found; user="
            in caplog.text
        )

    def test_manage_correct_action_options_shown(self):
        pass

    def test_manage_invalid_action_chosen(self):
        pass

    def test_delete_callback_invoked(self):
        pass

    def test_complete_callback_invoked(self):
        pass

    def test_start_callback_invoked(self):
        pass
