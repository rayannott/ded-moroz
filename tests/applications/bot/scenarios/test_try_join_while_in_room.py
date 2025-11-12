import pytest
from pytest import LogCaptureFixture

from src.applications.bot.callbacks.join import JoinCallback
from src.models.user import User
from src.repositories.database import DatabaseRepository


class TestJoinWhileInRoom:
    """Joining a room when already in one.

    Given:
    - a registered user
    - a user is already in a room
    When:
    - the user tries to join another room
    Then:
    - the bot should inform the user that they must leave the current room first.
    """

    @pytest.fixture
    def join_callback(self, bot_mock, moroz_integrated) -> JoinCallback:
        return JoinCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_join_while_in_room(
        self,
        join_callback: JoinCallback,
        message_factory,
        user_mock: User,
        database_repo: DatabaseRepository,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message = message_factory(text="/join")
        created_user = database_repo.create_user(
            user_mock.id, user_mock.username, user_mock.name
        )
        created_room = database_repo.create_room(
            created_by_user_id=created_user.id,
            room_name="Test Room",
        )
        database_repo.join_room(user_id=created_user.id, room_id=created_room.id)

        # WHEN
        that_user = database_repo.get_user(created_user.id)
        join_callback.process(message, that_user)

        # THEN
        bot_mock.send_message.assert_called_once_with(
            created_user.id,
            f"You have already joined the room {created_room.display_short_code}. Please /leave it first.",
        )
