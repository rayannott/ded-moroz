from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User

HELP_MESSAGE = """Available commands:
/start
/join
/help
/name
/me
/create
/manage
/leave
"""


class HelpCallback(Callback):
    def process(self, user: User, *, message: types.Message):
        logger.info(f"/help from {user}")
        self.bot.send_message(
            user.id,
            HELP_MESSAGE,
        )
