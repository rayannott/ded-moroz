from unittest.mock import MagicMock

import pytest
import telebot
from telebot import types


@pytest.fixture
def bot_mock() -> telebot.TeleBot:
    return MagicMock(spec=telebot.TeleBot)


@pytest.fixture
def message_factory():
    def _factory(
        chat_id=12345,
        first_name="TestUser",
        username="testuser",
        text="Hello",
        is_bot=False,
    ):
        chat = MagicMock(spec=types.Chat)
        chat.id = chat_id
        chat.first_name = first_name
        chat.username = username

        user = MagicMock(spec=types.User)
        user.is_bot = is_bot

        message = MagicMock(spec=types.Message)
        message.chat = chat
        message.from_user = user
        message.text = text
        return message

    return _factory
