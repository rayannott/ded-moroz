from unittest import mock

import pytest
from pytest import LogCaptureFixture
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.start import StartCallback
from src.shared.exceptions import UserNotFound


class TestStartCallback:
    @pytest.fixture(scope="function")
    def user_from_message_patched(self, user_mock):
        with mock.patch(
            "src.applications.bot.callbacks.start.user_from_message",
            return_value=user_mock,
        ) as patched:
            yield patched

    def test_process_wrap_greet_again(
        self,
        bot_mock,
        message_factory,
        moroz_mock,
        user_mock,
        user_from_message_patched,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message_mock = message_factory()
        user_mock.id = 12345
        user_mock.display_name = "TestUser42"
        user_mock.__str__.return_value = "this-usr"
        moroz_mock.get_user.return_value = user_mock
        # WHEN
        StartCallback(bot_mock, moroz_mock).process_wrap(message_mock)
        # THEN
        user_from_message_patched.assert_called_once_with(message_mock)
        bot_mock.send_message.assert_called_once_with(
            12345, "Welcome back, TestUser42!"
        )
        assert "/start from this-usr" in caplog.text

    def test_process_wrap_create_user(
        self,
        bot_mock,
        message_factory,
        moroz_mock,
        user_mock,
        user_from_message_patched,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message_mock = message_factory()
        user_mock.id = 12345
        user_mock.display_name = "TestUser42"
        user_mock.__str__.return_value = "this-usr"
        moroz_mock.get_user.side_effect = UserNotFound
        moroz_mock.create_user.return_value = user_mock
        # WHEN
        StartCallback(bot_mock, moroz_mock).process_wrap(message_mock)
        # THEN
        user_from_message_patched.assert_called_once_with(message_mock)
        bot_mock.send_message.assert_called_once_with(
            12345, "Welcome, TestUser42! You have been registered."
        )
        moroz_mock.create_user.assert_called_once_with(user_mock)
        assert "/start from this-usr" in caplog.text
