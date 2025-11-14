from loguru import logger

from src.applications.bot.callbacks.management.base import ManagementCallback
from src.applications.bot.utils import remove_keyboard
from src.models.room import Room
from src.models.user import User
from src.shared.exceptions import RoomTooSmall


class PlayCallback(ManagementCallback):
    def process_management(self, user: User, room: Room):
        logger.info(f"Play action chosen by {user} in {room}")

        try:
            target_pairs = self.moroz.start_game_in_room(room)
        except RoomTooSmall:
            logger.debug(
                f"Attempt to start game in too small {room.id=} by user {user}"
            )
            self.bot.send_message(
                user.id,
                "Cannot start the game: not enough players in the room (need at least 2).",
                reply_markup=remove_keyboard(),
            )
            return
        except Exception:
            logger.opt(exception=True).error(
                f"Error starting game in {room.id=} by user {user}"
            )
            self.bot.send_message(
                user.id, "Internal error.", reply_markup=remove_keyboard()
            )
            return

        for giver, receiver in target_pairs:
            logger.debug(f"Notifying {giver} about their target {receiver}")
            self.bot.send_message(
                giver.id,
                f"The game in room {room.display_short_code} has started! You are to give a gift to {receiver.display_name} 🎁",
            )

        participants = ", ".join(
            f"{u.display_name} (@{u.username})" for u, _ in target_pairs
        )
        self.bot.send_message(
            user.id,
            f"The game in room {room.display_short_code} has started! All participants ({participants}) have been notified privately.",
            reply_markup=remove_keyboard(),
        )
        logger.debug(f"Game started in room {room} by user {user}")
