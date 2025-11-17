from unittest import mock

import pytest
from pytest import LogCaptureFixture

from src.applications.bot.callbacks.management.complete import CompleteCallback
from src.applications.bot.callbacks.management.play import PlayCallback
from src.repositories.database import DatabaseRepository
from src.services.moroz import Moroz
from tests.utils import Regex


class TestStartCompleteGame:
    """Start and complete the game.

    Given:
    - a number of registered users
    - a room created by a different user (the manager)
    When:
    - the manager starts the game in that room
    Then:
    - messages are sent to all room members with their targets
    - the room's state is updated to reflect that the game has started
    - the targets have been inserted into the database
    - (quick sanity check) each user's name is mentioned once as a target and once as a seeker in the logs
    When:
    - the manager completes the game in that room
    Then:
    - the room's state is updated to reflect that the game has completed
    - a completion message is sent to the manager and all participants
    """

    @pytest.fixture
    def start_game_callback(self, bot_mock, database_repo) -> PlayCallback:
        moroz_allow_duets = Moroz(
            database_repository=database_repo,
            max_rooms_managed_by_user=2,
            min_players_to_start_game=2,  # allow duets for testing
        )
        return PlayCallback(bot=bot_mock, moroz=moroz_allow_duets)

    @pytest.fixture
    def complete_game_callback(self, bot_mock, moroz_integrated) -> CompleteCallback:
        return CompleteCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_try_start_game_lonely_manager(
        self,
        start_game_callback: PlayCallback,
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        # GIVEN
        manager = database_repo.create_user(id=301, username="manager", name="Manager")
        room = database_repo.create_room(created_by_user_id=manager.id)

        manager = database_repo.get_user(manager.id)

        # WHEN
        start_game_callback.process_management(manager, room)

        # THEN
        bot_mock.send_message.assert_called_once_with(
            manager.id,
            Regex("Cannot start the game.+not enough players.+"),
            reply_markup=mock.ANY,
        )

    def test_start_game_in_room(
        self,
        start_game_callback: PlayCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
        caplog: LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        manager = database_repo.create_user(id=401, username="manager", name="Manager")
        player_ids = [200 + i for i in range(5)]
        room = database_repo.create_room(created_by_user_id=manager.id)
        players = [
            database_repo.create_user(
                id=id_, username=f"player{i + 1}", name=f"Player{id_}"
            )
            for i, id_ in enumerate(player_ids)
        ]
        for player in players:
            database_repo.join_room(user_id=player.id, room_id=room.id)
        players = [database_repo.get_user(player.id) for player in players]
        manager = database_repo.get_user(manager.id)

        # WHEN
        start_game_callback.process_management(manager, room)

        # THEN
        room_after = database_repo.get_room(room.id)
        assert room_after.started_dt is not None
        assert room_after.completed_dt is None
        player_calls = [
            mock.call(
                player.id,
                Regex("The game.+has started! You are to give a gift to.+"),
            )  # TODO use localization to avoid duplication
            for player in players
        ]
        bot_mock.send_message.assert_has_calls(player_calls, any_order=True)
        assert bot_mock.mock_calls[-1] == mock.call.send_message(
            manager.id,
            Regex(r".+game.+started.+All participants.+notified.+"),
            reply_markup=mock.ANY,
        )

        # each user's name is mentioned once as a target and once as a seeker in the logs
        for player in players:
            mentions_as_giver = sum(
                1
                for record in caplog.records
                if f"Notifying {player}" in record.message
            )
            mentions_as_receiver = sum(
                1 for record in caplog.records if f"target {player}" in record.message
            )
            assert mentions_as_giver == 1
            assert mentions_as_receiver == 1

        # quick sanity check of the target assignments
        targets = [database_repo.get_target(room.id, player.id) for player in players]
        assert len(targets) == len(players)
        assert {t.id for t in targets} == {player.id for player in players}

    def test_manager_plays_duet(
        self,
        start_game_callback: PlayCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        # GIVEN
        manager = database_repo.create_user(id=601, username="manager", name="Manager")
        player = database_repo.create_user(id=602, username="player1", name="Player602")
        room = database_repo.create_room(created_by_user_id=manager.id)
        database_repo.join_room(user_id=player.id, room_id=room.id)
        database_repo.join_room(user_id=manager.id, room_id=room.id)
        manager = database_repo.get_user(manager.id)
        player = database_repo.get_user(player.id)
        # WHEN
        start_game_callback.process_management(manager, room)
        # THEN
        room_after = database_repo.get_room(room.id)
        assert room_after.started_dt is not None
        assert room_after.completed_dt is None
        bot_mock.send_message.assert_any_call(
            manager.id,
            Regex("The game.+has started! You are to give a gift to.+"),
        )
        bot_mock.send_message.assert_any_call(
            player.id,
            Regex("The game.+has started! You are to give a gift to.+"),
        )
        bot_mock.send_message.assert_any_call(
            manager.id,
            Regex(r".+game.+started.+All participants.+notified.+"),
            reply_markup=mock.ANY,
        )
        managers_target = database_repo.get_target(room.id, manager.id)
        players_target = database_repo.get_target(room.id, player.id)
        assert managers_target.id == player.id
        assert players_target.id == manager.id

    def test_complete_game_in_room(
        self,
        start_game_callback: PlayCallback,
        complete_game_callback: CompleteCallback,
        message_factory,
        database_repo: DatabaseRepository,
        bot_mock,
    ):
        # GIVEN
        manager = database_repo.create_user(id=501, username="manager", name="Manager")
        player_ids = [300 + i for i in range(3)]
        room = database_repo.create_room(created_by_user_id=manager.id)
        players = [
            database_repo.create_user(
                id=id_, username=f"player{i + 1}", name=f"Player{id_}"
            )
            for i, id_ in enumerate(player_ids)
        ]
        for player in players:
            database_repo.join_room(user_id=player.id, room_id=room.id)
        players = [database_repo.get_user(player.id) for player in players]
        manager = database_repo.get_user(manager.id)

        # Start the game first
        start_game_callback.process_management(manager, room)

        # WHEN: complete the game
        complete_game_callback.process_management(manager, room)
        # THEN
        room_after = database_repo.get_room(room.id)
        assert room_after.started_dt is not None
        assert room_after.completed_dt is not None

        calls = [
            mock.call.send_message(
                manager.id,
                Regex(r".+game.+completed successfully.+"),
                reply_markup=mock.ANY,
            )
        ]
        bot_mock.assert_has_calls(calls, any_order=True)
