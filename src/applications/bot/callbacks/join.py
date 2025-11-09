from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User
from src.models.room import Room
from src.applications.bot.utils import text
from src.shared.exceptions import (
    RoomNotFound,
    AlreadyInRoom,
    UserNotFound,
)


class JoinCallback(Callback):
    """
    Join a room by room code.

    show how the user will be displayed to others in the room
    and ask to set /name if their name is potentially unclear
    """

    def process(self, message: types.Message):
        usr = User.from_message(message)
        logger.info(f"/join from {usr}")

        try:
            user_actual = self.moroz.get_user(usr)
        except UserNotFound:
            self.bot.send_message(
                message.chat.id,
                "You are not registered yet. Please /start to register.",
            )
            return

        if user_actual.room_id is not None:
            self.bot.send_message(
                message.chat.id,
                f"You have already joined some room ({user_actual.room_id}). Please /leave it first.",
            )
            return

        answer = self.bot.send_message(
            message.chat.id,
            "Please enter the room ID you want to join:",
        )
        self.bot.register_next_step_handler(
            answer,
            self._handle_room_code_entered,
            user=usr,
        )

    def _handle_room_code_entered(
        self,
        message: types.Message,
        user: User,
    ):
        chosen_text = text(message)
        try:
            room_short_code = int(chosen_text)
        except ValueError:
            self.bot.send_message(
                message.chat.id,
                "Invalid room ID format. Please enter a numeric room ID.",
            )
            logger.info(f"Invalid room ID format entered by {user}: {chosen_text!r}")
            return
        
        logger.info(f"User {user} joining room with code {room_short_code}")

        try:
            joined_room = self.moroz.join_room_by_short_code(
                user=user,
                room_short_code=room_short_code,
            )
        except UserNotFound:
            logger.critical(
                "UserNotFound raised when joining room; should not have reached here"
            )
            self.bot.send_message(
                message.chat.id,
                "You are not registered yet. Please /start to register first.",
            )
            return
        except RoomNotFound:
            self.bot.send_message(
                message.chat.id,
                f"Room with ID {room_short_code:04d} not found.",
            )
            return
        except AlreadyInRoom:
            logger.critical(
                "AlreadyInRoom raised when joining room; should not have reached here"
            )
            self.bot.send_message(
                message.chat.id,
                "You have already joined some room. Please /leave it first.",
            )
            return

        self.bot.send_message(
            message.chat.id,
            f"You have successfully joined the room {room_short_code:04d}! 🎉",
        )

        self._notify_manager(user, joined_room)

    def _notify_manager(self, user: User, room: Room):
        logger.info(f"Notifying manager about {user} joining {room}")
        self.bot.send_message(
            room.manager_user_id,
            f"User {user.display_name} (@{user.username}) has joined your room {room.display_short_code}.",
        )
