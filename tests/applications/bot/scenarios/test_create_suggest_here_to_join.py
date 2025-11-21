import re

import pytest
from pytest import LogCaptureFixture
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.create import CreateCallback
from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestCreateSuggestHereToJoin:
    """Test creating rooms with suggestion to join.

    Given:
    - a registered user
    When:
    - the user creates a room
    Then:
    - the user is suggested to join the room (IF they are not already in a room)
    """

    @pytest.fixture
    def callback(self, bot_mock, moroz_integrated) -> CreateCallback:
        return CreateCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_create_room_suggest_here_to_join(
        self,
        callback: CreateCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        user = database_repo.create_user(
            id=301, username="suggestuser", name="Suggest User"
        )
        message = message_factory(text="/create")
        # WHEN
        callback.process(user, message=message)
        # THEN
        bot_mock.send_message.assert_called_once_with(
            user.id,
            Regex(r"Room created.+ID: `\d{4}`.+here.+", flags=re.DOTALL),
            parse_mode="MarkdownV2",
        )
        assert "Room created" in caplog.text

    def test_create_room_no_suggest_here(
        self,
        callback: CreateCallback,
        message_factory,
        database_repo: DatabaseRepository,
        create_manager_room: tuple[User, Room],
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN (manager in the room)
        manager, room = create_manager_room
        database_repo.join_room(manager.id, room.id)
        message = message_factory(text="/create")
        manager = database_repo.get_user(manager.id)
        # WHEN
        callback.process(manager, message=message)
        # THEN
        bot_mock.send_message.assert_called_once_with(
            manager.id,
            Regex(r"Room created.+ID: `\d{4}`.+", flags=re.DOTALL),
            parse_mode="MarkdownV2",
        )
        assert "here" not in bot_mock.send_message.call_args.args[1]
