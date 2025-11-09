from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User
from src.models.room import Room
from src.applications.bot.utils import text
from src.shared.exceptions import (
    RoomNotFound,
    AlreadyInRoom,
    GameAlreadyStarted,
    GameAlreadyCompleted,
)


class JoinCallback(Callback):
    """
    Join a room by room code.
    """

    def process(self, message: types.Message, user: User):
        if user.room_id is not None:
            room = self.moroz.get_room(user.room_id)
            self.bot.send_message(
                message.chat.id,
                f"You have already joined some room {room.display_short_code}. Please /leave it first.",
            )
            return

        answer = self.bot.send_message(
            message.chat.id,
            "Please enter the room ID you want to join:",
        )
        self.bot.register_next_step_handler(
            answer,
            self._handle_room_code_entered,
            user=user,
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

        room_short_code_str = f"{room_short_code:04d}"
        logger.info(f"User {user} joining room with code {room_short_code_str}")

        try:
            joined_room = self.moroz.join_room_by_short_code(
                user=user,
                room_short_code=room_short_code,
            )
        except RoomNotFound:
            self.bot.send_message(
                message.chat.id,
                f"Room with ID {room_short_code_str} not found.",
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
        except GameAlreadyStarted:
            self.bot.send_message(
                message.chat.id,
                f"The game in room {room_short_code_str} has already started. You cannot join now.",
            )
            return
        except GameAlreadyCompleted:
            self.bot.send_message(
                message.chat.id,
                f"The game in room {room_short_code_str} has already completed. You cannot join now.",
            )
            return

        self.bot.send_message(
            message.chat.id,
            f"You have successfully joined the room {room_short_code_str}! 🎉",
        )

        self._notify_manager(user, joined_room)

    def _notify_manager(self, user: User, room: Room):
        logger.info(f"Notifying manager about {user} joining {room}")
        self.bot.send_message(
            room.manager_user_id,
            f"User {user.display_name} (@{user.username}) has joined your room {room.display_short_code}",
        )
