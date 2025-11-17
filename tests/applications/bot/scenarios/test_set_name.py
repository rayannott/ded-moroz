import pytest

from src.applications.bot.callbacks.join import JoinCallback
from src.applications.bot.callbacks.name import NameCallback
from src.repositories.database import DatabaseRepository


class TestSetName:
    """Update the user's name.

    Given:
    - a registered user u1; a room manager u2
    When:
    - the user u1 updates their name
    Then:
    - u1's name is updated in the system
    - a confirmation message is sent to u1
    When:
    - u1 joins a room managed by u2
    Then:
    - u2 gets notified of u1 joining with the updated name
    """

    @pytest.fixture
    def join_callback(self, bot_mock, moroz_integrated) -> JoinCallback:
        return JoinCallback(bot=bot_mock, moroz=moroz_integrated)

    @pytest.fixture
    def name_callback(self, bot_mock, moroz_integrated):
        return NameCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_set_name_ok(
        self,
        join_callback: JoinCallback,
        name_callback: NameCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        # GIVEN
        manager = database_repo.create_user(id=201, username="manager", name="Manager")
        user = database_repo.create_user(
            id=202, username="simpleuser", name="Simple User"
        )
        room = database_repo.create_room(created_by_user_id=manager.id)
        name_message = message_factory(text="/name", chat_id=user.id)
        # WHEN
        name_callback.process(user, message=name_message)
        _, (_answer, callback_fn), _kwargs = (
            bot_mock.register_next_step_handler.mock_calls[0]
        )
        # THEN
        assert callback_fn == name_callback._set_name

        # WHEN (user enters new name)
        new_name_message = message_factory(text="Complicated User")
        name_callback._set_name(new_name_message, user)
        # THEN
        updated_user = database_repo.get_user(user.id)
        assert updated_user.name == "Complicated User"
        bot_mock.send_message.assert_called_with(
            user.id,
            "Your name has been set to 'Complicated User'.",
        )

        # WHEN: user joins the room
        join_message = message_factory(text="/join", chat_id=user.id)
        join_callback.process(updated_user, message=join_message)
        # THEN
        _, (_answer, callback_fn), _kwargs = (
            bot_mock.register_next_step_handler.mock_calls[1]
        )
        assert callback_fn == join_callback._handle_room_code_entered
        # WHEN (user enters room code)
        join_room_message = message_factory(text=room.display_short_code)
        callback_fn(join_room_message, updated_user)
        # THEN (the manager is notified about the join with the updated name)
        bot_mock.send_message.assert_called_with(
            manager.id,
            f"User Complicated User (@simpleuser) has joined your room {room.display_short_code}",
        )

    @pytest.mark.parametrize(
        "invalid_name,reason",
        [
            ("", "cannot be empty"),
            (" \n  \t\t", "cannot be empty"),
            ("ab432", "can only contain letters and spaces"),
            ("a" * 51, "cannot be longer than 50 characters"),
        ],
    )
    def test_set_name_invalid(
        self,
        name_callback: NameCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
        invalid_name: str,
        reason: str,
    ):
        # GIVEN
        user = database_repo.create_user(
            id=202, username="simpleuser", name="Simple User"
        )
        name_message = message_factory(text="/name", chat_id=user.id)
        # WHEN
        name_callback.process(user, message=name_message)
        _, (_answer, callback_fn), _kwargs = (
            bot_mock.register_next_step_handler.mock_calls[0]
        )
        # THEN
        assert callback_fn == name_callback._set_name

        # WHEN (user enters invalid new name)
        invalid_name_message = message_factory(
            text=invalid_name
        )  # Empty name is invalid
        name_callback._set_name(invalid_name_message, user)
        # THEN
        updated_user = database_repo.get_user(user.id)
        assert updated_user.name == "Simple User"  # Name should not be changed
        bot_mock.send_message.assert_called_with(
            user.id,
            f"Invalid name: {reason}. Please try again with a different name.",
        )
