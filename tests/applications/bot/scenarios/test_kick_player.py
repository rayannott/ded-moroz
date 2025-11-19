from unittest import mock

import pytest
from pytest import LogCaptureFixture

from src.applications.bot.callbacks.management.kick import KickCallback
from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestKickPlayer:
    """Manager kicks player from the room.

    Given:
        - registered users: u0 (manager), u1 (member)
        - a room created by u0, with u1 as a member
    When:
        - the manager u0 kicks u1 from the room
    Then:
        - u1 should receive a notification about being kicked
        - u1 should no longer be a member of the room

    When:
        - the player is already not in the room (e.g., left by themselves) when the manager tries to kick them
    Then:
        - the manager should be informed that the player is already not in the room
        - a warning should be logged
    """

    @pytest.fixture
    def kick_callback(self, bot_mock, moroz_integrated) -> KickCallback:
        return KickCallback(bot=bot_mock, moroz=moroz_integrated)

    @pytest.fixture
    def create_manager_member_room(
        self, database_repo: DatabaseRepository, create_manager_room: tuple[User, Room]
    ) -> tuple[User, User, Room]:
        manager, room = create_manager_room
        member = database_repo.create_user(
            id=1001,
            username="u1_member",
            name="Member 1",
        )

        database_repo.join_room(member.id, room.id)

        manager = database_repo.get_user(manager.id)
        member = database_repo.get_user(member.id)
        room = database_repo.get_room(room.id)

        return manager, member, room

    # --- happy path ---

    def test_kick_player_success(
        self,
        kick_callback: KickCallback,
        create_manager_member_room: tuple[User, User, Room],
        database_repo: DatabaseRepository,
        bot_mock,
        message_factory,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        manager, member, room = create_manager_member_room

        # WHEN (manager initiates kick)
        kick_callback.process_management(manager, room)

        # THEN – a next step handler is registered
        _, (_, callback_fn), kwargs = bot_mock.register_next_step_handler.mock_calls[0]
        assert callback_fn == kick_callback._handle_player_selected

        # WHEN (manager selects the member to kick)
        answer_message = message_factory(text=member.formal_display_name)
        callback_fn(answer_message, **kwargs)

        # THEN – logs contain kicking info
        assert "kicking" in caplog.text

        # member should no longer be in the room
        updated_member = database_repo.get_user(member.id)
        assert updated_member.room_id is None

        # calls to bot:
        to_manager_prompt = mock.call(
            manager.id,
            "Select a player to kick:",
            reply_markup=mock.ANY,
        )
        to_manager_confirmation = mock.call(
            manager.id,
            Regex(r"Player .+ has been kicked from the room .+\."),
            reply_markup=mock.ANY,
        )
        to_kicked_player = mock.call(
            member.id,
            Regex(r"You have been kicked from the room .+ by its manager .+\."),
        )

        bot_mock.send_message.assert_has_calls(
            [to_manager_prompt, to_manager_confirmation, to_kicked_player]
        )

    def test_kick_no_players_in_room(
        self,
        kick_callback: KickCallback,
        database_repo: DatabaseRepository,
        create_manager_room: tuple[User, Room],
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN: manager + room with no players returned by moroz
        manager, room = create_manager_room
        # WHEN
        kick_callback.process_management(manager, room)
        # THEN
        bot_mock.send_message.assert_called_with(
            manager.id,
            "There are no players in the room to kick.",
            reply_markup=mock.ANY,
        )
        assert "No players to kick" in caplog.text

    def test_kick_cancel_selection(
        self,
        kick_callback: KickCallback,
        create_manager_member_room: tuple[User, User, Room],
        bot_mock,
        message_factory,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        manager, _, room = create_manager_member_room

        # manager initiates kick to register handler
        kick_callback.process_management(manager, room)
        _, (_, callback_fn), kwargs = bot_mock.register_next_step_handler.mock_calls[0]

        # WHEN – manager presses "Cancel"
        cancel_message = message_factory(text="Cancel")
        callback_fn(cancel_message, **kwargs)

        # THEN
        bot_mock.send_message.assert_called_with(
            manager.id,
            "Kick action cancelled.",
            reply_markup=mock.ANY,
        )
        assert "Kick action cancelled by" in caplog.text

    def test_kick_invalid_selection(
        self,
        kick_callback: KickCallback,
        create_manager_member_room: tuple[User, User, Room],
        bot_mock,
        message_factory,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        manager, member, room = create_manager_member_room

        player_repr_to_id = {member.formal_display_name: member.id}
        invalid_choice = "Some Other Player"
        message = message_factory(text=invalid_choice)

        # WHEN – manager selects something not in player_repr_to_id
        kick_callback._handle_player_selected(
            message,
            user=manager,
            room=room,
            player_repr_to_id=player_repr_to_id,
        )

        # THEN
        bot_mock.send_message.assert_called_with(
            manager.id,
            "Invalid selection. Please try the kick command again.",
            reply_markup=mock.ANY,
        )
        assert "Invalid player selection" in caplog.text
        assert invalid_choice in caplog.text

    def test_kick_player_already_not_in_room(
        self,
        kick_callback: KickCallback,
        create_manager_member_room: tuple[User, User, Room],
        database_repo: DatabaseRepository,
        bot_mock,
        message_factory,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        manager, member, room = create_manager_member_room
        database_repo.leave_room(member.id)

        player_repr_to_id = {member.formal_display_name: member.id}
        message = message_factory(text=member.formal_display_name)

        # WHEN – manager tries to kick a player already not in room
        kick_callback._handle_player_selected(
            message,
            user=manager,
            room=room,
            player_repr_to_id=player_repr_to_id,
        )

        # THEN – manager is informed
        bot_mock.send_message.assert_called_with(
            manager.id,
            Regex(r"Player .+ is already not in the room.+"),
            reply_markup=mock.ANY,
        )
        # and a warning is logged
        assert "was not in room" in caplog.text
