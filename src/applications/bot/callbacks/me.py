from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User
from src.shared.exceptions import UserNotFound, RoomNotFound


class MeCallback(Callback):
    """
    Show information about the user.

    - if any, the room the user is currently in
       and the number of participants there
    - the user's custom name (if set by /name)
    - if any, the rooms the user is managing
    """

    def process(self, message: types.Message):
        usr = User.from_message(message)
        logger.info(f"/me from {usr}")
        try:
            this_user = self.moroz.get_user(usr)
        except UserNotFound:
            self.bot.send_message(
                message.chat.id,
                "You are not registered yet. Please /start to register.",
            )
            return
        msg = self.moroz.get_user_information(this_user)
        self.bot.send_message(message.chat.id, msg)
