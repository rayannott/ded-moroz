from unittest import mock

import pytest

from src.applications.bot.callbacks.management.delete import DeleteCallback
from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from src.shared.exceptions import RoomNotFound
from tests.utils import Regex


class TestRoomDeletedNotifyMembers:
    """Notifying members when a room is deleted.

    Given:
        - registered users: u0 (manager), u1, u2 (members)
        - a room created by u0, with u1 and u2 as members
    When:
        - the manager u0 deletes the room
    Then:
        - u1 and u2 should receive a notification about the room deletion
    """

    @pytest.fixture
    def delete_callback(self, bot_mock, moroz_integrated) -> DeleteCallback:
        return DeleteCallback(bot=bot_mock, moroz=moroz_integrated)

    @pytest.mark.parametrize("prompt_response", ["Confirm", "Cancel"])
    def test_delete_notify_members(
        self,
        delete_callback: DeleteCallback,
        create_manager_room: tuple[User, Room],
        database_repo: DatabaseRepository,
        message_factory,
        bot_mock,
        prompt_response: str,
    ):
        # GIVEN
        manager, room = create_manager_room
        member1 = database_repo.create_user(id=202, username="member1", name="Member1")
        member2 = database_repo.create_user(id=203, username="member2", name="Member2")

        database_repo.join_room(user_id=member1.id, room_id=room.id)
        database_repo.join_room(user_id=member2.id, room_id=room.id)

        # WHEN
        manager = database_repo.get_user(manager.id)
        delete_callback.process_management(manager, room)

        # THEN
        _, obj, _ = bot_mock.register_next_step_handler.mock_calls[0]
        callback_fn = obj[1]
        assert callback_fn == delete_callback._confirm_deletion

        # WHEN
        callback_fn(message_factory(text=prompt_response), manager, room)

        # THEN
        if prompt_response == "Cancel":
            bot_mock.send_message.assert_called_with(
                manager.id,
                f"Room deletion for {room.display_short_code} cancelled.",
                reply_markup=mock.ANY,
            )
            return

        with pytest.raises(RoomNotFound):
            database_repo.get_room(room.id)

        calls = [
            mock.call(
                manager.id,
                Regex(r"Room.+\(2 players\).+deleted successfully.+"),
                reply_markup=mock.ANY,
            )
        ]
        calls.extend(
            (
                mock.call(
                    member.id,
                    f"The room {room.display_short_code} you were in has been deleted "
                    "by its manager Manager (@manager). You have been removed from the room.",
                )
                for member in (member1, member2)
            )
        )
        bot_mock.send_message.assert_has_calls(calls, any_order=True)
        assert bot_mock.send_message.call_count == 4
