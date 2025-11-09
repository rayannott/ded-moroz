from loguru import logger
from telebot import types

from src.applications.bot.callbacks.management._base import ManagementCallback
from src.applications.bot.utils import remove_keyboard
from src.models.room import Room
from src.models.user import User


class CompleteCallback(ManagementCallback):
    def process_management(self, message: types.Message, user: User, room: Room):
        logger.info(f"Complete action chosen by {user} in {room}")
        # self.bot.send_message(
        #     message.chat.id,
        #     "Complete functionality is not implemented yet.",
        #     reply_markup=remove_keyboard(),
        # )
        try:
            users_in_just_completed_room = self.moroz.complete_game_in_room(room)
        except Exception:
            logger.opt(exception=True).error(
                f"Error completing game in {room.id=} by user {user}"
            )
            self.bot.send_message(
                message.chat.id, "Internal error.", reply_markup=remove_keyboard()
            )
            return
        self.bot.send_message(
            message.chat.id,
            f"The game in room {room.short_code:04d} has been completed successfully. 🎉",
            reply_markup=remove_keyboard(),
        )
        logger.info(f"Game in room {room} completed by {user}")

        for user in users_in_just_completed_room:
            logger.debug(f"Notifying user {user} about game completion in {room}")
            self.bot.send_message(
                user.id,
                f"The game in room {room.short_code:04d} has been completed by its manager. Thank you for participating!",
            )
