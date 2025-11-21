import re
from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
import time_machine
from pytest_loguru.plugin import caplog  # noqa: F401

from src.applications.bot.callbacks.create import CreateCallback
from src.applications.bot.callbacks.here import ALLOW_HERE_CONTEXT_SECONDS, HereCallback
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestCreateHereCallback:
    @pytest.fixture
    def here_callback(self, bot_mock, moroz_integrated) -> HereCallback:
        return HereCallback(bot=bot_mock, moroz=moroz_integrated)

    @pytest.fixture
    def create_callback(self, bot_mock, moroz_integrated) -> CreateCallback:
        return CreateCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_join_just_created_room_success(
        self,
        create_callback: CreateCallback,
        here_callback: HereCallback,
        database_repo: DatabaseRepository,
        message_factory,
        bot_mock,
        caplog: pytest.LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        # TODO: make timezone aware + also change the models
        travelling_to = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        user = database_repo.create_user(id=501, username="creator", name="Creator")
        with time_machine.travel(travelling_to, tick=False):
            create_callback.process(user, message=message_factory("/create"))

        # WHEN
        with time_machine.travel(
            travelling_to + timedelta(seconds=ALLOW_HERE_CONTEXT_SECONDS - 1),
            tick=False,
        ):
            here_callback.process(user, message=message_factory("/here"))

        # THEN
        bot_mock.send_message.assert_has_calls(
            [
                mock.call(
                    user.id,
                    Regex(".+created.+here.+", flags=re.DOTALL),
                    parse_mode="MarkdownV2",
                ),
                mock.call(user.id, "You have joined the room you just created."),
            ]
        )
        assert "joined just created room" in caplog.text

    def test_join_just_created_room_too_late(
        self,
        create_callback: CreateCallback,
        here_callback: HereCallback,
        database_repo: DatabaseRepository,
        message_factory,
        bot_mock,
        caplog: pytest.LogCaptureFixture,  # noqa: F811
    ):
        travelling_to = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        user = database_repo.create_user(id=501, username="creator", name="Creator")
        with time_machine.travel(travelling_to, tick=False):
            create_callback.process(user, message=message_factory("/create"))

        # WHEN
        with time_machine.travel(
            travelling_to + timedelta(seconds=ALLOW_HERE_CONTEXT_SECONDS + 1),
            tick=False,
        ):
            here_callback.process(user, message=message_factory("/here"))

        # THEN
        user = database_repo.get_user(user.id)
        bot_mock.send_message.assert_has_calls(
            [
                mock.call(
                    user.id,
                    Regex(".+created.+here.+", flags=re.DOTALL),
                    parse_mode="MarkdownV2",
                ),
                mock.call(
                    user.id,
                    (msg := "Couldn't determine what to do with the /here command."),
                ),
            ]
        )
        assert msg in caplog.text
        assert "joined just created room" not in caplog.text

    def test_join_just_created_room_already_in_room(
        self,
        create_callback: CreateCallback,
        here_callback: HereCallback,
        database_repo: DatabaseRepository,
        message_factory,
        bot_mock,
        caplog: pytest.LogCaptureFixture,  # noqa: F811
    ):
        # GIVEN
        travelling_to = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        user = database_repo.create_user(id=501, username="creator", name="Creator")
        with time_machine.travel(travelling_to, tick=False):
            create_callback.process(user, message=message_factory("/create"))
        another_room = database_repo.create_room(created_by_user_id=user.id)
        database_repo.join_room(user.id, another_room.id)
        user = database_repo.get_user(user.id)

        # WHEN
        with time_machine.travel(
            travelling_to + timedelta(seconds=ALLOW_HERE_CONTEXT_SECONDS - 1),
            tick=False,
        ):
            here_callback.process(user, message=message_factory("/here"))

        # THEN
        user = database_repo.get_user(user.id)
        bot_mock.send_message.assert_has_calls(
            [
                mock.call(
                    user.id,
                    Regex(".+created.+", flags=re.DOTALL),
                    parse_mode="MarkdownV2",
                ),
                mock.call(
                    user.id,
                    (msg := "Couldn't determine what to do with the /here command."),
                ),
            ]
        )
        assert msg in caplog.text
        assert "joined just created room" not in caplog.text
        assert "already in a room" in caplog.text
