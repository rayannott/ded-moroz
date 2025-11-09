from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.shared.exceptions import UserNotFound, NotInRoom

from src.models.user import User


class LeaveCallback(Callback):
    """
    Leave the room that user is currently in, if any.

    notify that room's manager.
    """

    def process(self, message: types.Message):
        usr = User.from_message(message)
        logger.info(f"/leave from {usr}")
        try:
            self.moroz.leave_room(usr)
        except UserNotFound:
            self.bot.send_message(
                message.chat.id,
                "You are not registered yet. Please /start to register.",
            )
            return
        except NotInRoom:
            self.bot.send_message(
                message.chat.id,
                "You are not currently in any room.",
            )
            return

        self.bot.send_message(
            message.chat.id,
            "You have successfully left the room! 🎉",
        )
