from loguru import logger

from src.applications.bot.callbacks.management.base import ManagementCallback
from src.applications.bot.utils import remove_keyboard
from src.models.room import Room
from src.models.user import User


class KickCallback(ManagementCallback):
    def process_management(self, user: User, room: Room):
        logger.info(f"Kick action chosen by {user} in {room}")
        self.bot.send_message(
            user.id,
            "Kick functionality is not implemented yet.",
            reply_markup=remove_keyboard(),
        )
