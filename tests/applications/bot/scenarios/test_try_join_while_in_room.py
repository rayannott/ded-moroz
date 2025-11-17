import pytest
from pytest import LogCaptureFixture

from src.applications.bot.callbacks.join import JoinCallback
from src.models.room import Room
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
        create_manager_room: tuple[User, Room],
        database_repo: DatabaseRepository,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message = message_factory(text="/join")
        created_user, created_room = create_manager_room
        database_repo.join_room(user_id=created_user.id, room_id=created_room.id)
        this_user = database_repo.get_user(created_user.id)

        # WHEN
        join_callback.process(this_user, message=message)

        # THEN
        bot_mock.send_message.assert_called_once_with(
            this_user.id,
            f"You have already joined the room {created_room.display_short_code}. Please /leave it first.",
        )
