from telebot import types
from loguru import logger

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
    def process(self, message: types.Message, user: User):
        logger.info(f"/help from {user}")
        self.bot.send_message(
            message.chat.id,
            HELP_MESSAGE,
        )
