import re
from unittest import mock

import pytest

from src.applications.bot.callbacks.me import MeCallback
from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestGetUserInformation:
    @pytest.fixture
    def me_callback(self, bot_mock, moroz_integrated) -> MeCallback:
        return MeCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_user_not_in_any_room_and_not_manager(
        self,
        me_callback: MeCallback,
        bot_mock,
        message_factory,
        database_repo: DatabaseRepository,
    ):
        # GIVEN: user with no rooms and not in any room
        user = database_repo.create_user(
            id=402,
            username="loner",
            name="Loner",
        )
        user = database_repo.get_user(user.id)

        # WHEN
        me_callback.process(user, message=message_factory())

        # THEN
        bot_mock.send_message.assert_called_once_with(
            user.id,
            Regex(
                r"You are .+!\s+Status: not in any room\.",
                flags=re.DOTALL,
            ),
        )

    def test_user_manages_active_room_but_not_in_any_room(
        self,
        me_callback: MeCallback,
        bot_mock,
        message_factory,
        database_repo: DatabaseRepository,
        create_manager_room: tuple[User, Room],
    ):
        # GIVEN: manager created a room but is not joined to it (no room_id)
        manager, _ = create_manager_room
        # NOTE: we intentionally do NOT call join_room for the manager here

        # WHEN
        me_callback.process(manager, message=message_factory())

        # THEN
        bot_mock.send_message.assert_called_once_with(
            manager.id,
            Regex(
                r"You are Manager.+!"
                r".+Active rooms you manage: \d{4}" + r".+Status: not in any room\.",
                flags=re.DOTALL,
            ),
        )

    def test_user_in_room_but_not_manager(
        self,
        me_callback: MeCallback,
        bot_mock,
        database_repo: DatabaseRepository,
        message_factory,
        create_manager_room: tuple[User, Room],
    ):
        # GIVEN: participant is in a room, but manages no rooms
        _, room = create_manager_room
        participant = database_repo.create_user(
            id=403,
            username="participant",
            name="P1",
        )
        database_repo.join_room(user_id=participant.id, room_id=room.id)
        participant = database_repo.get_user(participant.id)
        room = database_repo.get_room(room.id)

        # WHEN
        me_callback.process(participant, message=message_factory())

        # THEN:
        # - no "Status: not in any room."
        # - includes "You are in Room ..."
        bot_mock.send_message.assert_called_once_with(
            participant.id,
            Regex(
                r"You are P1.+!" r".+You are in Room \d{4}" r".+managed by: Manager.+",
                flags=re.DOTALL,
            ),
        )

    def test_two_managers_in_each_others_rooms(
        self,
        me_callback: MeCallback,
        bot_mock,
        database_repo: DatabaseRepository,
        message_factory,
    ):
        # GIVEN: two managers, each joined to the other's room
        manager1 = database_repo.create_user(
            id=404, username="manager1", name="Manager1"
        )
        r1 = database_repo.create_room(created_by_user_id=manager1.id)
        manager2 = database_repo.create_user(
            id=405, username="manager2", name="Manager2"
        )
        r2 = database_repo.create_room(created_by_user_id=manager2.id)

        database_repo.join_room(user_id=manager1.id, room_id=r2.id)
        database_repo.join_room(user_id=manager2.id, room_id=r1.id)

        manager1 = database_repo.get_user(manager1.id)
        manager2 = database_repo.get_user(manager2.id)

        # WHEN
        me_callback.process(manager1, message=message_factory())
        me_callback.process(manager2, message=message_factory())

        # THEN
        bot_mock.send_message.assert_has_calls(
            [
                mock.call(
                    manager1.id,
                    Regex(
                        r"You are Manager1.+!"
                        r".+Active rooms you manage: \d{4}"
                        r".+You are in Room \d{4}"
                        r".+managed by: Manager2.+",
                        flags=re.DOTALL,
                    ),
                ),
                mock.call(
                    manager2.id,
                    Regex(
                        r"You are Manager2.+!"
                        r".+Active rooms you manage: \d{4}"
                        r".+You are in Room \d{4}"
                        r".+managed by: Manager1.+",
                        flags=re.DOTALL,
                    ),
                ),
            ],
        )
