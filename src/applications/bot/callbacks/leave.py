from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.room import Room
from src.models.user import User
from src.shared.exceptions import NotInRoom


class LeaveCallback(Callback):
    def process(self, user: User, *, message: types.Message):
        logger.info(f"/leave from {user}")
        try:
            left_room = self.moroz.leave_room(user_id=user.id)
        except NotInRoom:
            self.bot.send_message(
                user.id,
                "You are not currently in any room.",
            )
            return

        self.bot.send_message(
            user.id,
            "You have successfully left the room! 🎉",
        )

        self._notify_manager(user, left_room)

    def _notify_manager(self, user: User, room: Room):
        logger.debug(f"Notifying manager about {user} leaving {room}")
        self.bot.send_message(
            room.manager_user_id,
            f"User {user.formal_display_name} has left your room {room.display_short_code}",
        )
