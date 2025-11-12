from unittest import mock

import pytest
from pytest import LogCaptureFixture
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.base import Callback
from src.models.user import User
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class AnyCallback(Callback):
    def process(self, message, user):
        pass


class TestRejectNonRegistered:
    @pytest.fixture(scope="function")
    def user_from_message_patched(self, user_mock):
        with mock.patch(
            "src.applications.bot.callbacks.base.user_from_message",
            return_value=user_mock,
        ) as patched:
            yield patched

    @pytest.fixture
    def callback(self, bot_mock, moroz_integrated) -> AnyCallback:
        return AnyCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_user_not_found(
        self,
        callback: AnyCallback,
        message_factory,
        user_mock: User,
        user_from_message_patched,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message = message_factory()
        user_from_message_patched.return_value = user_mock
        # WHEN / THEN
        callback.process_wrap(message)
        assert "is not registered." in caplog.text
        bot_mock.send_message.assert_called_once_with(
            message.chat.id,
            Regex(r".+not registered.+"),
        )

    def test_user_exists(
        self,
        callback: AnyCallback,
        message_factory,
        user_mock: User,
        database_repo: DatabaseRepository,
        user_from_message_patched,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        database_repo.create_user(user_mock.id, user_mock.username, user_mock.name)
        message = message_factory()
        user_from_message_patched.return_value = user_mock
        # WHEN
        callback.process_wrap(message)
        # THEN
        assert "AnyCallback from User(id=123456; @testuser, Test): Hello" in caplog.text
