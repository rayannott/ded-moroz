from loguru import logger

from src.applications.bot.callbacks.management.base import ManagementCallback
from src.applications.bot.utils import remove_keyboard


class InfoCallback(ManagementCallback):
    def process_management(self, user, room):
        logger.info(f"Info action chosen by {user} in {room}")
        msg = self.moroz.get_room_information(room.id)
        self.bot.send_message(
            user.id,
            msg,
            reply_markup=remove_keyboard(),
        )
