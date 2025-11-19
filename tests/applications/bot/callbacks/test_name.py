from unittest import mock

from pytest import LogCaptureFixture
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.name import NameCallback


class TestNameCallback:
    def test_process(
        self,
        message_factory,
        bot_mock,
        moroz_mock,
        user_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message = message_factory(text="/name")
        answer_message = message_factory(text="some name")
        user_mock.__str__.return_value = "this-usr"
        bot_mock.send_message.return_value = answer_message
        cb = NameCallback(bot_mock, moroz_mock)

        # WHEN
        cb.process(user_mock, message=message)

        # THEN
        assert "/name from this-usr" in caplog.text
        bot_mock.send_message.assert_called_once_with(
            user_mock.id,
            "Please provide the name you want to use.",
        )
        bot_mock.register_next_step_handler.assert_called_once_with(
            answer_message,
            cb._set_name,
            user=user_mock,
        )

    def test__set_name(
        self,
        message_factory,
        bot_mock,
        moroz_mock,
        user_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message = message_factory(text=" Someone \t  ")
        user_mock.__str__.return_value = "this-usr"

        with mock.patch(
            "src.applications.bot.callbacks.name.text",
            return_value=message.text,
        ) as text_mock:
            # WHEN
            NameCallback(bot_mock, moroz_mock)._set_name(message, user_mock)

        # THEN
        text_mock.assert_called_once_with(message)
        moroz_mock.update_name.assert_called_once_with(user_mock.id, "Someone")
        bot_mock.send_message.assert_called_once_with(
            user_mock.id,
            "Your name has been set to 'Someone'.",
        )

        assert "Setting name for this-usr to 'Someone'" in caplog.text
        assert "Name for this-usr set to 'Someone'" in caplog.text
