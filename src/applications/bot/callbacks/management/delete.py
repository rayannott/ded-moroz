from loguru import logger
from telebot import types

from src.applications.bot.callbacks.management._base import ManagementCallback
from src.applications.bot.utils import remove_keyboard
from src.models.room import Room
from src.models.user import User
from src.shared.exceptions import RoomNotFound


class DeleteCallback(ManagementCallback):
    def process_management(self, message: types.Message, user: User, room: Room):
        logger.debug(f"Delete action chosen by {user} in {room}")
        try:
            users_in_just_deleted_room = self.moroz.delete_room(
                room_id=room.id,
            )
        except RoomNotFound:
            logger.opt(exception=True).error(
                f"Error deleting {room.id=} by user {user}"
            )
            self.bot.send_message(
                message.chat.id, "Internal error.", reply_markup=remove_keyboard()
            )
            return

        self.bot.send_message(
            message.chat.id,
            f"Room {room.short_code:04d} ({len(users_in_just_deleted_room)} players) deleted successfully. 🎉",
            reply_markup=remove_keyboard(),
        )
        logger.info(f"Room {room} deleted by {user}")

        self._cleanup_after_room_deletion(room, user, users_in_just_deleted_room)

    def _notify_one_user(self, user: User, ex_room: Room):
        logger.debug(f"Notifying user {user} about {ex_room} deletion")
        self.bot.send_message(
            user.id,
            f"The room {ex_room.short_code:04d} you were in has been deleted by its manager. You have been removed from the room.",
        )

    def _cleanup_after_room_deletion(
        self,
        room: Room,
        user: User,
        users_in_room: list[User],
    ):
        logger.info(
            f"Cleaning up after deletion of {room.id=} with {len(users_in_room)} players"
        )
        for user in users_in_room:
            self._notify_one_user(user, room)
