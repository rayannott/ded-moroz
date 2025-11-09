from loguru import logger
from telebot import types

from src.applications.bot.callbacks.management._base import ManagementCallback
from src.applications.bot.utils import remove_keyboard
from src.models.room import Room
from src.models.user import User
from src.shared.exceptions import RoomNotFound


class PlayCallback(ManagementCallback):
    def process_management(self, message: types.Message, user: User, room: Room):
        logger.info(f"Play action chosen by {user} in room {room}")
        # self.bot.send_message(
        #     message.chat.id,
        #     "Play functionality is not implemented yet.",
        #     reply_markup=remove_keyboard(),
        # )

        try:
            target_pairs = self.moroz.start_game_in_room(room)
        except RoomNotFound:
            logger.opt(exception=True).error(
                f"Error retrieving users in {room.id=} by user {user}"
            )
            self.bot.send_message(
                message.chat.id, "Internal error.", reply_markup=remove_keyboard()
            )
            return

        for giver, receiver in target_pairs:
            logger.debug(f"Notifying {giver} about their target {receiver}")
            self.bot.send_message(
                giver.id,
                f"The game has started! You are to give a gift to {receiver.display_name} 🎁",
            )
