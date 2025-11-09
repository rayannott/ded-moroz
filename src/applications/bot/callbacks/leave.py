from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.shared.exceptions import NotInRoom

from src.models.user import User


class LeaveCallback(Callback):
    """
    Leave the room that user is currently in, if any.

    notify that room's manager.
    """

    def process(self, message: types.Message, user: User):
        logger.info(f"/leave from {user}")
        try:
            self.moroz.leave_room(user)
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
