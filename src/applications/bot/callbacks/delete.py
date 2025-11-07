from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class DeleteCallback(Callback):
    """
    Delete one of the rooms managed by the user.

    - show keyboard of the (unfinished) rooms that this user managing
    """

    def process(self, message: types.Message):
        logger.info(f"/delete from {User.from_message(message)}")
        self.bot.send_message(message.chat.id, "Deleting a room is not implemented yet.")
