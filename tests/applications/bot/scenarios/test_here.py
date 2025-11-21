import re
from unittest import mock
from datetime import datetime, timezone, timedelta
from pytest_loguru.plugin import caplog  # noqa: F401

import pytest
import time_machine

from src.applications.bot.callbacks.here import HereCallback
from src.applications.bot.callbacks.create import CreateCallback
from src.repositories.database import DatabaseRepository
from tests.utils import Regex


class TestHereCallback:
    @pytest.fixture
    def here_callback(self, bot_mock, moroz_integrated) -> HereCallback:
        return HereCallback(bot=bot_mock, moroz=moroz_integrated)

    @pytest.fixture
    def create_callback(self, bot_mock, moroz_integrated) -> CreateCallback:
        return CreateCallback(bot=bot_mock, moroz=moroz_integrated)

    def test_option_join_just_created_room_success(
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
        with time_machine.travel(travelling_to):
            create_callback.process(user, message=message_factory("/create"))

        # WHEN
        with time_machine.travel(travelling_to + timedelta(seconds=59)):
            here_callback.process(user, message=message_factory("/here"))

        # THEN
        bot_mock.send_message.assert_has_calls(
            [
                mock.call(
                    user.id,
                    Regex(".+created.+/here.+", flags=re.DOTALL),
                    parse_mode="MarkdownV2",
                ),
                mock.call(user.id, "You have joined the room you just created."),
            ]
        )
        assert "joined just created room" in caplog.text

    def test_option_join_just_created_room_too_late(
        self,
        create_callback: CreateCallback,
        here_callback: HereCallback,
        database_repo: DatabaseRepository,
        message_factory,
        bot_mock,
        caplog: pytest.LogCaptureFixture,  # noqa: F811
    ):
        # TODO
        pass

    def test_option_join_just_created_room_failure_already_in_room(
        self,
        create_callback: CreateCallback,
        here_callback: HereCallback,
        database_repo: DatabaseRepository,
        create_manager_room,
        message_factory,
        bot_mock,
        caplog: pytest.LogCaptureFixture,  # noqa: F811
    ):
        # TODO
        pass
