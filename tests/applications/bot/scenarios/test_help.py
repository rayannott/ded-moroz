import pytest

from src.applications.bot.callbacks.help import HelpCallback
from src.repositories.database import DatabaseRepository


class TestHelpCallback:
    @pytest.fixture
    def help_callback(self, bot_mock, moroz_integrated) -> HelpCallback:
        return HelpCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_help_message_sent(
        self,
        help_callback: HelpCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        # GIVEN
        user = database_repo.create_user(id=101, username="helpuser", name="Help User")
        # WHEN
        help_callback.process(user, message=message_factory("/help"))
        # THEN
        help_text = bot_mock.send_message.call_args.args[1]
        for cmd in [
            "/create",
            "/join",
            "/manage",
            "/leave",
            "/help",
            "/start",
            "/name",
            "/me",
        ]:
            assert cmd in help_text

        assert "share feedback with me" not in help_text

    def test_help_message_admin_username(
        self,
        help_callback: HelpCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        # GIVEN
        user = database_repo.create_user(
            id=102, username="helpuser2", name="Help User 2"
        )
        help_callback.moroz.admin_username = "adminuser"
        # WHEN
        help_callback.process(user, message=message_factory("/help"))
        # THEN
        help_text = bot_mock.send_message.call_args.args[1]
        assert "share feedback with me: @adminuser" in help_text

    def test_help_message_admin_name_and_username(
        self,
        help_callback: HelpCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        # GIVEN
        user = database_repo.create_user(
            id=103, username="helpuser3", name="Help User 3"
        )
        help_callback.moroz.admin_name = "Admin Name"
        help_callback.moroz.admin_username = "adminuser"
        # WHEN
        help_callback.process(user, message=message_factory("/help"))
        # THEN
        help_text = bot_mock.send_message.call_args.args[1]
        assert "share feedback with me: Admin Name (@adminuser)" in help_text
