import pytest

from src.applications.bot.callbacks.management.play import PlayCallback
from src.repositories.database import DatabaseRepository


class TestStartGameInRoom:
    """Start the game.

    Given:
    - a number of registered users
    - a room created by one of the users (the manager)
    When:
    - the manager starts the game in that room
    Then:
    - messages are sent to all room members with their targets
    - the room's state is updated to reflect that the game has started
    """

    # TODO(test): also test when RoomTooSmall

    @pytest.fixture
    def start_game_callback(self, bot_mock, moroz_integrated) -> PlayCallback:
        return PlayCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_start_game(
        self,
        start_game_callback: PlayCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        pass
