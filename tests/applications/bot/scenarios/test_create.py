import re
from unittest import mock
import pytest
from pytest import LogCaptureFixture
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.create import CreateCallback
from src.models.user import User
from src.repositories.database import DatabaseRepository
from src.shared.exceptions import UserNotFound
from tests.utils import Regex


class TestCreateCallbackIntegration:
    @pytest.fixture
    def callback(self, bot_mock, moroz_integrated) -> CreateCallback:
        return CreateCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_create_room_success(
        self,
        callback: CreateCallback,
        message_factory,
        user_mock: User,
        database_repo: DatabaseRepository,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        database_repo.create_user(user_mock.id, user_mock.username, user_mock.name)
        message = message_factory(text="/create")
        # WHEN
        callback.process(message, user_mock)
        # THEN
        managed_rooms = database_repo.get_active_rooms_managed_by_user(user_mock.id)
        assert len(managed_rooms) == 1
        bot_mock.send_message.assert_called_once_with(
            message.chat.id,
            Regex(r"Room created.+ID: `\d{4}`.+", flags=re.DOTALL),
            parse_mode="MarkdownV2",
        )
        assert "Room created" in caplog.text

    def test_create_room_max_reached(
        self,
        callback: CreateCallback,
        message_factory,
        user_mock: User,
        database_repo: DatabaseRepository,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN (max rooms per user is 2)
        database_repo.create_user(user_mock.id, user_mock.username, user_mock.name)
        message = message_factory(text="/create")
        _on_not_created_log_part = (
            "Maximum number of rooms reached: user created_by_user_id=123456"
        )

        # WHEN / THEN
        callback.process(message, user_mock)
        managed_rooms = database_repo.get_active_rooms_managed_by_user(user_mock.id)
        assert len(managed_rooms) == 1
        assert _on_not_created_log_part not in caplog.text

        callback.process(message, user_mock)
        managed_rooms = database_repo.get_active_rooms_managed_by_user(user_mock.id)
        assert len(managed_rooms) == 2
        assert _on_not_created_log_part not in caplog.text
        assert "Room created" in caplog.text

        callback.process(message, user_mock)
        managed_rooms = database_repo.get_active_rooms_managed_by_user(user_mock.id)
        assert len(managed_rooms) == 2
        assert _on_not_created_log_part in caplog.text

        bot_mock.send_message.assert_has_calls(
            [
                mock.call(
                    message.chat.id,
                    Regex(r"Room created.+ID: `\d{4}`.+", flags=re.DOTALL),
                    parse_mode="MarkdownV2",
                ),
                mock.call(
                    message.chat.id,
                    Regex(r"Room created.+ID: `\d{4}`.+", flags=re.DOTALL),
                    parse_mode="MarkdownV2",
                ),
                mock.call(
                    message.chat.id,
                    Regex(
                        r"You have reached the maximum number of rooms you can create.+",
                        flags=re.DOTALL,
                    ),
                ),
            ]
        )
