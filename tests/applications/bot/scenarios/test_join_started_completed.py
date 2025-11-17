import pytest
from pydantic_extra_types.pendulum_dt import DateTime

from src.applications.bot.callbacks.join import JoinCallback
from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository


class TestJoinStartedCompletedGame:
    """Joining a room in which a game has already started or completed.

    Given:
    - a registered user
    - a room where the game has already started or completed
    When:
    - the user tries to join that room
    Then:
    - the bot should inform the user that the game has already started or completed and they cannot join
    """

    @pytest.fixture
    def join_callback(self, bot_mock, moroz_integrated) -> JoinCallback:
        return JoinCallback(bot=bot_mock, moroz=moroz_integrated)

    @pytest.fixture
    def create_user_room(self, database_repo: DatabaseRepository, user_mock: User):
        created_user = database_repo.create_user(
            user_mock.id, user_mock.username, user_mock.name
        )
        created_room = database_repo.create_room(created_by_user_id=created_user.id)
        this_user = database_repo.get_user(created_user.id)
        return this_user, created_room

    def test_join_started_game(
        self,
        join_callback: JoinCallback,
        message_factory,
        create_user_room: tuple[User, Room],
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        # GIVEN
        this_user, created_room = create_user_room
        code_chosen_msg = message_factory(text=created_room.display_short_code)
        database_repo.set_game_started(created_room.id, started_dt=DateTime.utcnow())

        # WHEN
        this_user = database_repo.get_user(this_user.id)
        join_callback._handle_room_code_entered(
            message=code_chosen_msg,
            user=this_user,
        )

        # THEN
        bot_mock.send_message.assert_called_with(
            this_user.id,
            f"The game in room {created_room.display_short_code} has already started. You cannot join now.",
        )

    def test_join_completed_game(
        self,
        join_callback: JoinCallback,
        message_factory,
        create_user_room: tuple[User, Room],
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        # GIVEN
        this_user, created_room = create_user_room
        code_chosen_msg = message_factory(text=created_room.display_short_code)
        database_repo.set_game_completed(
            created_room.id, completed_dt=DateTime.utcnow()
        )

        # WHEN
        this_user = database_repo.get_user(this_user.id)
        join_callback._handle_room_code_entered(
            message=code_chosen_msg,
            user=this_user,
        )

        # THEN
        bot_mock.send_message.assert_called_with(
            this_user.id,
            f"The game in room {created_room.display_short_code} has already completed. You cannot join now.",
        )
