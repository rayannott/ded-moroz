from unittest import mock

import pytest
from pytest import LogCaptureFixture
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.base import Callback
from src.shared.exceptions import UserNotFound


class AnyCallback(Callback):
    def process(self, message, user):
        pass


class TestCallback:
    @pytest.fixture(scope="function")
    def user_from_message_patched(self, user_mock):
        with mock.patch(
            "src.applications.bot.callbacks.base.user_from_message",
            return_value=user_mock,
        ) as patched:
            yield patched

    def test_process_wrap_user_none(
        self,
        message_factory,
        bot_mock,
        moroz_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):  # noqa: F811
        # GIVEN
        message = message_factory()
        message.from_user = None
        # WHEN
        AnyCallback(bot_mock, moroz_mock).process_wrap(message)
        # THEN
        bot_mock.send_message.assert_not_called()
        moroz_mock.get_user.assert_not_called()
        assert "has no from_user" in caplog.text

    def test_process_wrap_user_is_bot(
        self,
        message_factory,
        bot_mock,
        moroz_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message = message_factory()
        message.from_user.is_bot = True
        # WHEN
        AnyCallback(bot_mock, moroz_mock).process_wrap(message)
        # THEN
        bot_mock.send_message.assert_not_called()
        moroz_mock.get_user.assert_not_called()
        assert "Ignoring message from bot user" in caplog.text

    def test_process_wrap_user_exists(
        self,
        message_factory,
        bot_mock,
        moroz_mock,
        user_mock,
        user_from_message_patched,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message = message_factory(text="hullo")
        usr_obj = mock.MagicMock()
        user_from_message_patched.return_value = usr_obj
        moroz_mock.get_user.return_value = user_mock
        # WHEN
        AnyCallback(bot_mock, moroz_mock).process_wrap(message)
        # THEN
        moroz_mock.get_user.assert_called_once_with(usr_obj)
        user_from_message_patched.assert_called_once_with(message)
        assert "AnyCallback from this-user: hullo" in caplog.text

    def test_process_wrap_user_not_found(
        self,
        message_factory,
        bot_mock,
        moroz_mock,
        user_mock,
        user_from_message_patched,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message = message_factory()
        usr_obj = mock.MagicMock()
        user_from_message_patched.return_value = usr_obj
        usr_obj.__str__ = mock.MagicMock(return_value="non-existent-user")  # type: ignore[method-assign]
        moroz_mock.get_user.side_effect = UserNotFound
        # WHEN
        AnyCallback(bot_mock, moroz_mock).process_wrap(message)
        # THEN
        moroz_mock.get_user.assert_called_once()
        user_from_message_patched.assert_called_once_with(message)
        bot_mock.send_message.assert_called_once_with(
            message.chat.id,
            "You are not registered yet. Please /start to register.",
        )
        assert "User non-existent-user is not registered." in caplog.text
