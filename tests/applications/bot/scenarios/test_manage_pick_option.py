from unittest import mock

import pytest
from pydantic_extra_types.pendulum_dt import DateTime
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.management.manage import (
    ManageActions,
    ManageCallback,
)
from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestManagePickOption:
    """Manager manages the room."""

    @pytest.fixture
    def manage_callback(self, bot_mock, moroz_integrated) -> ManageCallback:
        return ManageCallback(bot=bot_mock, moroz=moroz_integrated)

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
        create_manager_room,
    ):
        # GIVEN
        manager_user, created_room = create_manager_room
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

    def test_manage_no_active_rooms_suggest_history(
        self,
        manage_callback: ManageCallback,
        database_repo: DatabaseRepository,
        message_factory,
        bot_mock,
    ):
        # GIVEN
        manager_user = database_repo.create_user(
            id=201, username="manager", name="Manager"
        )
        # create a finished room
        past_room = database_repo.create_room(created_by_user_id=manager_user.id)
        database_repo.set_game_started(past_room.id, DateTime.utcnow().add(minutes=10))
        database_repo.set_game_completed(past_room.id, DateTime.utcnow().add(days=4))
        message = message_factory(text="/manage")
        # WHEN
        manage_callback.process(manager_user, message=message)
        # THEN
        bot_mock.send_message.assert_called_once_with(
            manager_user.id,
            "You are not managing any active rooms currently. However, you have managed 1 rooms in the past. Use /history to see them.",
        )

    def test_manage_manager_initiates_manage_has_room(
        self,
        manage_callback: ManageCallback,
        message_factory,
        create_manager_room: tuple[User, Room],
        get_keyboard_patch,
        bot_mock,
    ):
        # GIVEN
        manager_user, created_room = create_manager_room
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
            [created_room.display_short_code, ManageActions.CANCEL.value]
        )

    def test_manage_manager_cancels(
        self,
        manage_callback: ManageCallback,
        message_factory,
        create_manager_room: tuple[User, Room],
        bot_mock,
    ):
        # GIVEN
        manager_user, created_room = create_manager_room
        message = message_factory(text="/manage")
        # WHEN
        manage_callback.process(manager_user, message=message)
        _, (_, callback_fn), _ = bot_mock.register_next_step_handler.mock_calls[0]
        answer_message = message_factory(text=ManageActions.CANCEL.value)
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
        create_manager_room: tuple[User, Room],
        caplog: pytest.LogCaptureFixture,  # noqa: F811
        bot_mock,
    ):
        # GIVEN
        manager_user, created_room = create_manager_room
        message = message_factory(text="/manage")
        # WHEN
        manage_callback.process(manager_user, message=message)
        _, (_, callback_fn), _ = bot_mock.register_next_step_handler.mock_calls[0]
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

    def test_manage_correct_action_options_new_room(
        self,
        manage_callback: ManageCallback,
        message_factory,
        create_manager_room: tuple[User, Room],
        get_keyboard_patch,
        bot_mock,
    ):
        # GIVEN (a new room and its manager)
        manager_user, created_room = create_manager_room
        room_chosen_message = message_factory(text=created_room.display_short_code)
        kb_mock = mock.MagicMock()
        get_keyboard_patch.return_value = kb_mock
        # WHEN
        manage_callback._handle_room_chosen(
            room_chosen_message,
            user=manager_user,
            code_to_room={created_room.short_code: created_room},
        )
        # THEN
        get_keyboard_patch.assert_called_once_with(
            [
                ManageActions.DELETE.value,
                ManageActions.START.value,
                ManageActions.KICK_PLAYER.value,
                ManageActions.INFO.value,
                ManageActions.CANCEL.value,
            ],
            row_width=2,
        )
        bot_mock.send_message.assert_called_with(
            manager_user.id,
            f"You are managing room {created_room.display_short_code}. Please choose an action:",
            reply_markup=kb_mock,
        )

    def test_manage_correct_action_options_in_progress_room(
        self,
        manage_callback: ManageCallback,
        message_factory,
        create_manager_room: tuple[User, Room],
        database_repo: DatabaseRepository,
        get_keyboard_patch,
        bot_mock,
    ):
        # GIVEN (a room in progress and its manager)
        manager_user, created_room = create_manager_room
        # game started:
        database_repo.set_game_started(created_room.id, DateTime.utcnow())
        room_chosen_message = message_factory(text=created_room.display_short_code)
        kb_mock = mock.MagicMock()
        get_keyboard_patch.return_value = kb_mock
        # WHEN
        this_room = database_repo.get_room(created_room.id)
        manage_callback._handle_room_chosen(
            room_chosen_message,
            user=manager_user,
            code_to_room={created_room.short_code: this_room},
        )
        # THEN
        get_keyboard_patch.assert_called_once_with(
            [
                ManageActions.COMPLETE.value,
                ManageActions.INFO.value,
                ManageActions.CANCEL.value,
            ],
            row_width=2,
        )
        bot_mock.send_message.assert_called_with(
            manager_user.id,
            f"You are managing room {created_room.display_short_code}. Please choose an action:",
            reply_markup=kb_mock,
        )

    def test_manage_invalid_action_chosen(
        self,
        manage_callback: ManageCallback,
        message_factory,
        create_manager_room: tuple[User, Room],
        bot_mock,
    ):
        # GIVEN
        manager_user, created_room = create_manager_room
        action_chosen_message = message_factory(text="Some invalid action")
        # WHEN
        manage_callback._handle_action_chosen(
            action_chosen_message,
            user=manager_user,
            room=created_room,
        )
        # THEN
        bot_mock.send_message.assert_called_once_with(
            manager_user.id,
            Regex("Invalid action selected.+"),
            reply_markup=mock.ANY,
        )
