import re
from unittest import mock

import pytest
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.app import BotApp
from tests.utils import Regex


class TestBotStarted:
    @pytest.fixture
    def bot_app(self, bot_mock, moroz_integrated) -> BotApp:
        with mock.patch(
            "src.applications.bot.app.telebot.TeleBot", return_value=bot_mock
        ):
            bot_app = BotApp(api_token="TEST_TOKEN", moroz=moroz_integrated)
        return bot_app

    def test_bot_started(
        self,
        bot_app: BotApp,
        bot_mock,
        caplog,  # noqa: F811
    ):
        # WHEN
        bot_app.run()
        # THEN
        bot_mock.infinity_polling.assert_called_once()
        assert "Bot started" in caplog.text
        assert "Bot stopped" in caplog.text

    def test_dont_notify_admin_when_no_admin_user_id(
        self,
        bot_app: BotApp,
        bot_mock,
        caplog,  # noqa: F811
    ):
        # WHEN (no admin_user_id set by default)
        bot_app.run()
        # THEN
        bot_mock.send_message.assert_not_called()
        assert "Bot started" in caplog.text
        assert "Bot stopped" in caplog.text

    def test_notify_admin_when_admin_user_id_set(
        self,
        bot_app: BotApp,
        bot_mock,
        caplog,  # noqa: F811
    ):
        # GIVEN
        bot_app.moroz.admin_user_id = 99999
        # WHEN
        bot_app.run()
        # THEN
        bot_mock.send_message.assert_has_calls(
            [
                mock.call(
                    99999,
                    Regex("Bot has just started.+", flags=re.DOTALL),
                ),
                mock.call(
                    99999,
                    "Bot has just stopped.",
                ),
            ]
        )
        assert "Bot started" in caplog.text
        assert "Bot stopped" in caplog.text
