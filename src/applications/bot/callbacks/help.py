from telebot import types
from loguru import logger

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


HELP_MESSAGE = """Available commands:
/start
/create
/join
/help
/play
/name
/me
/leave
"""


class HelpCallback(Callback):
    def process(self, message: types.Message):
        logger.info(f"/help from {User.from_message(message)}")
        self.bot.send_message(
            message.chat.id,
            HELP_MESSAGE,
        )
