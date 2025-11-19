import pytest

from src.applications.bot.callbacks.start import StartCallback
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestStartBot:
    @pytest.fixture
    def start_callback(self, bot_mock, moroz_integrated) -> StartCallback:
        return StartCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_start_register(
        self,
        start_callback: StartCallback,
        database_repo: DatabaseRepository,
        message_factory,
        bot_mock,
    ):
        # GIVEN
        message = message_factory(text="/start", chat_id=1001, username="newuser")

        # WHEN
        start_callback.process_wrap(message)

        # THEN
        bot_mock.send_message.assert_called_once_with(
            1001,
            Regex("Welcome,.+registered.+"),
        )
        newly_registered_user = database_repo.get_user(1001)
        assert newly_registered_user is not None
        assert newly_registered_user.username == "newuser"

    def test_start_welcome_back(
        self,
        start_callback: StartCallback,
        database_repo: DatabaseRepository,
        message_factory,
        bot_mock,
    ):
        # GIVEN
        existing_user = database_repo.create_user(
            id=1002, username="existinguser", name="Existing User"
        )
        message = message_factory(
            text="/start", chat_id=existing_user.id, username=existing_user.username
        )

        # WHEN
        start_callback.process_wrap(message)

        # THEN
        bot_mock.send_message.assert_called_once_with(
            existing_user.id,
            Regex("Welcome back,.+"),
        )
