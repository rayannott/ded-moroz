from unittest import mock

import pytest
from pytest import LogCaptureFixture

from src.applications.bot.callbacks.join import JoinCallback
from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestJoinRoom:
    """Joining a room.

    Given:
    - a registered user
    - a room managed by them
    When(initiate):
    - the user tries to join the room
    Then:
    - the bot prompts the user to enter the room code

    When(enter code):
    - the user enters the correct room code
    Then:
    - the user is added to the room
    - the bot confirms the successful joining of the room
    """

    @pytest.fixture
    def join_callback(self, bot_mock, moroz_integrated) -> JoinCallback:
        return JoinCallback(bot=bot_mock, moroz=moroz_integrated)

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

    def test_join_ok(
        self,
        join_callback: JoinCallback,
        message_factory,
        create_user_room: tuple[User, Room],
        user_mock: User,
        database_repo: DatabaseRepository,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        this_user, created_room = create_user_room
        message = message_factory(text="/join")

        # WHEN (user initiates join)
        join_callback.process(this_user, message=message)

        # THEN
        _, (_answer, callback_fn), _kwargs = (
            bot_mock.register_next_step_handler.mock_calls[0]
        )
        assert callback_fn == join_callback._handle_room_code_entered

        # WHEN (user enters room code)
        answer_message = message_factory(text=created_room.display_short_code)
        callback_fn(answer_message, user=this_user)

        # THEN
        assert "joining room with code" in caplog.text
        first_call = mock.call(this_user.id, Regex("Please enter.+"))
        to_the_joinee = mock.call(
            this_user.id,
            Regex(".+successfully joined the room.+"),
        )
        to_the_manager = mock.call(
            this_user.id,
            Regex("User .+ has joined your room.+"),
        )
        bot_mock.send_message.assert_has_calls(
            [first_call, to_the_joinee, to_the_manager]
        )

    def test_join_invalid_code_format(
        self,
        join_callback: JoinCallback,
        message_factory,
        create_user_room: tuple[User, Room],
        user_mock: User,
        database_repo: DatabaseRepository,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        this_user, created_room = create_user_room
        message = message_factory(text="/join")

        # WHEN (user initiates join)
        join_callback.process(this_user, message=message)

        # THEN
        _, (_answer, callback_fn), _kwargs = (
            bot_mock.register_next_step_handler.mock_calls[0]
        )
        assert callback_fn == join_callback._handle_room_code_entered

        # WHEN (user enters invalid room code)
        answer_message = message_factory(text="invalid-code")
        callback_fn(answer_message, user=this_user)

        # THEN
        assert "Invalid room ID format entered" in caplog.text
        assert bot_mock.send_message.call_count == 2
        bot_mock.send_message.assert_called_with(
            this_user.id,
            Regex("Invalid room ID format.+"),
        )

    def test_join_room_not_found(
        self,
        join_callback: JoinCallback,
        message_factory,
        create_user_room: tuple[User, Room],
        user_mock: User,
        database_repo: DatabaseRepository,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        this_user, created_room = create_user_room
        message = message_factory(text="/join")

        # WHEN (user initiates join)
        join_callback.process(this_user, message=message)

        # THEN
        _, (_answer, callback_fn), _kwargs = (
            bot_mock.register_next_step_handler.mock_calls[0]
        )
        assert callback_fn == join_callback._handle_room_code_entered

        # WHEN (user enters non-existing room code)
        non_existing_code = f"{(created_room.short_code + 1) % 10000:04d}"
        answer_message = message_factory(text=non_existing_code)
        callback_fn(answer_message, user=this_user)

        # THEN
        assert bot_mock.send_message.call_count == 2
        bot_mock.send_message.assert_called_with(
            this_user.id, Regex(r"Room .+ not found\.")
        )
