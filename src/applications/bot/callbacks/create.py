from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class CreateCallback(Callback):
    """
    Create a new room.

    - show the room code
    - note that the manager is not automatically joined to the room;
      hence, suggest to /join
    """

    def process(self, message: types.Message):
        logger.info(f"/create from {User.from_message(message)}")
        self.bot.send_message(message.chat.id, "Room creation.")
