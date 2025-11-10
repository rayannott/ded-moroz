from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.room import Room
from src.models.user import User
from src.shared.exceptions import NotInRoom


class LeaveCallback(Callback):
    def process(self, message: types.Message, user: User):
        logger.info(f"/leave from {user}")
        try:
            self.moroz.leave_room(user)
        except NotInRoom:
            self.bot.send_message(
                message.chat.id,
                "You are not currently in any room.",
            )
            return

        self.bot.send_message(
            message.chat.id,
            "You have successfully left the room! 🎉",
        )

        # self._notify_manager(user, joined_room)

    # def _notify_manager(self, user: User, room: Room):
    #     logger.info(f"Notifying manager about {user} joining {room}")
    #     self.bot.send_message(
    #         room.manager_user_id,
    #         f"User {user.display_name} (@{user.username}) has joined your room {room.display_short_code}",
    #     )
