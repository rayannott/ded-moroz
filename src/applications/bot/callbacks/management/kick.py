from loguru import logger
from telebot import types

from src.applications.bot.callbacks.management._base import ManagementCallback
from src.applications.bot.utils import remove_keyboard
from src.models.room import Room
from src.models.user import User


class KickCallback(ManagementCallback):
    def process_management(self, message: types.Message, user: User, room: Room):
        logger.info(f"Kick action chosen by {user} in room {room}")
        self.bot.send_message(
            message.chat.id,
            "Kick functionality is not implemented yet.",
            reply_markup=remove_keyboard(),
        )
