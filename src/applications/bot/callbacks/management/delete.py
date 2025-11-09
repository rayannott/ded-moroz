from loguru import logger
from telebot import types

from src.applications.bot.callbacks.management._base import ManagementCallback
from src.applications.bot.utils import remove_keyboard
from src.models.room import Room
from src.models.user import User
from src.shared.exceptions import NotInRoom, RoomNotFound, UserNotFound


class DeleteCallback(ManagementCallback):
    def process_management(self, message: types.Message, user: User, room: Room):
        logger.debug(f"Delete action chosen by {user} in room {room}")
        try:
            users_in_room = self.moroz.database_repository.get_users_in_room(room.id)
            self.moroz.delete_room(
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
            f"Room {room.short_code:04d} ({len(users_in_room)} players) deleted successfully. 🎉",
            reply_markup=remove_keyboard(),
        )
        logger.info(f"Room {room} deleted by {user}")

        self._cleanup_after_room_deletion(room, user, users_in_room)

    def _clenup_one_user(self, user: User) -> bool:
        logger.debug(f"Cleaning up user {user} after room deletion")
        try:
            this_user = self.moroz.get_user(user)
        except UserNotFound:
            logger.opt(exception=True).error(
                f"Error cleaning up user {user} after room deletion"
            )
            return False

        logger.debug(f"Removing user {this_user} from room id={this_user.room_id}")
        try:
            self.moroz.leave_room(
                user,
            )
            return True
        except UserNotFound:
            logger.opt(exception=True).error(
                f"Error removing {this_user} from {this_user.room_id=} after room deletion"
            )
        except NotInRoom:
            logger.opt(exception=True).error(
                f"User {this_user} is not in any room during cleanup at room deletion"
            )
        return False

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
            if self._clenup_one_user(user):
                self._notify_one_user(user, room)
