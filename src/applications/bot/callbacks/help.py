from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User

HELP_MESSAGE = """Available commands:
/start - register yourself with the bot
/join - join an existing room
/help - show this help message
/name - set or change your display name
/me - show info about yourself (name, username, current room, etc.)
/create - create a new room
/manage - manage room(s) you created (if any)
/leave - leave the current room (if any)
"""


class HelpCallback(Callback):
    def process(self, user: User, *, message: types.Message):
        logger.info(f"/help from {user}")
        self.bot.send_message(
            user.id,
            HELP_MESSAGE,
        )
