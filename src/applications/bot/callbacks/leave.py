from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class LeaveCallback(Callback):
    """
    Leave the room that user is currently in, if any.

    notify that room's manager.
    """

    def process(self, message: types.Message):
        logger.info(f"/leave from {User.from_message(message)}")
        self.bot.send_message(message.chat.id, "Goodbye! See you next time.")
