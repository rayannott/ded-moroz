from loguru import logger
from telebot import types

from src.applications.bot.callbacks.management.base import ManagementCallback
from src.applications.bot.utils import remove_keyboard
from src.models.room import Room
from src.models.user import User


class CompleteCallback(ManagementCallback):
    def process_management(self, message: types.Message, user: User, room: Room):
        logger.info(f"Complete action chosen by {user} in {room}")
        users_in_just_completed_room = self.moroz.complete_game_in_room(room)

        self.bot.send_message(
            message.chat.id,
            f"The game in room {room.display_short_code} has been completed successfully. 🎉",
            reply_markup=remove_keyboard(),
        )
        logger.debug(f"Game in room {room} completed by {user}")

        for user in users_in_just_completed_room:
            logger.debug(f"Notifying user {user} about game completion in {room}")
            self.bot.send_message(
                user.id,
                f"The game in room {room.display_short_code} has been completed by its manager. Thank you for participating!",
            )
