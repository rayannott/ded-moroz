from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class NameCallback(Callback):
    """
    Set the name of the user,
    overriding `message.chat.first_name`.
    """

    def process(self, message: types.Message):
        logger.info(f"/name from {User.from_message(message)}")
        self.bot.send_message(message.chat.id, "Setting a name is not implemented yet.")
