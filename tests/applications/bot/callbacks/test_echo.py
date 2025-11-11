from pytest import LogCaptureFixture
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.echo import EchoCallback


class TestEchoCallback:
    def test_process(
        self,
        bot_mock,
        message_factory,
        user_mock,
        moroz_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message_mock = message_factory(text="/unknowncommand")
        # WHEN
        EchoCallback(bot_mock, moroz_mock).process(message_mock, user_mock)
        # THEN
        bot_mock.reply_to.assert_called_once_with(
            message_mock, "Unknown command '/unknowncommand'. Try /help."
        )
        assert "/echo from this-user" in caplog.text
