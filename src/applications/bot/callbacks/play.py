from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class PlayCallback(Callback):
    """
    Start a game in the chosen room.

    - show keyboard of the (unfinished) rooms that this user managing
    - on selecting a room (confirmation, etc.) send each user in that
        room their target user and set their target_user_id field accordingly
    - mark the game as completed
    """

    def process(self, message: types.Message):
        logger.info(f"/play from {User.from_message(message)}")
        self.bot.send_message(message.chat.id, "Playing a game.")
