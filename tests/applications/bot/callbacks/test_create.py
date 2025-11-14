from unittest import mock

from pytest import LogCaptureFixture
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.create import CreateCallback
from src.models.user import User
from src.shared.exceptions import MaxNumberOfRoomsReached


class TestCreateCallback:
    def test_process_created(
        self,
        message_factory,
        bot_mock,
        moroz_mock,
        user_mock: User,
        room_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message = message_factory(text="/create")
        moroz_mock.create_room.return_value = room_mock
        # WHEN
        CreateCallback(bot_mock, moroz_mock).process(user_mock, message=message)
        # THEN
        moroz_mock.create_room.assert_called_once_with(
            created_by_user_id=user_mock.id,
            room_name="New Room",
        )
        bot_mock.send_message.assert_called_once_with(
            user_mock.id,
            mock.ANY,
            parse_mode="MarkdownV2",
        )
        assert "/create from this-user" in caplog.text

    def test_process_max_rooms_reached(
        self,
        message_factory,
        bot_mock,
        moroz_mock,
        user_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        message = message_factory(text="/create")
        moroz_mock.create_room.side_effect = MaxNumberOfRoomsReached
        # WHEN
        CreateCallback(bot_mock, moroz_mock).process(user_mock, message=message)
        # THEN
        moroz_mock.create_room.assert_called_once_with(
            created_by_user_id=user_mock.id,
            room_name="New Room",
        )
        bot_mock.send_message.assert_called_once_with(
            user_mock.id,
            "You have reached the maximum number of rooms you can create. "
            "Please /manage and delete an existing room before creating a new one.",
        )
        assert "/create from this-user" in caplog.text
