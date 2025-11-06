from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class MeCallback(Callback):
    """
    Show information about the user.

    - if any, the room the user is currently in
       and the number of participants there
    - the user's custom name (if set by /name)
    - if any, the rooms the user is managing
    """
    def process(self, message: types.Message):
        logger.info(f"/me from {User.from_message(message)}")
        self.bot.send_message(message.chat.id, "You are you.")
