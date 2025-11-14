from loguru import logger

from src.applications.bot.callbacks.management.base import ManagementCallback
from src.applications.bot.utils import remove_keyboard
from src.models.room import Room
from src.models.user import User


class DeleteCallback(ManagementCallback):
    def process_management(self, user: User, room: Room):
        logger.info(f"Delete action chosen by {user} in {room}")
        users_in_just_deleted_room = self.moroz.delete_room(
            room_id=room.id,
        )
        self.bot.send_message(
            user.id,
            f"Room {room.display_short_code} ({len(users_in_just_deleted_room)} players) deleted successfully. 🎉",
            reply_markup=remove_keyboard(),
        )
        logger.debug(f"Room {room} deleted by {user}")

        self._notify_ex_members(room, user, users_in_just_deleted_room)

    def _notify_one_user(self, user: User, manager_user: User, ex_room: Room):
        logger.debug(f"Notifying user {user} about {ex_room} deletion")
        self.bot.send_message(
            user.id,
            f"The room {ex_room.display_short_code} you were in has been deleted by its manager {manager_user.formal_display_name}. "
            "You have been removed from the room.",
        )

    def _notify_ex_members(
        self,
        room: Room,
        manager_user: User,
        users_in_room: list[User],
    ):
        for user in users_in_room:
            self._notify_one_user(user, manager_user, room)
