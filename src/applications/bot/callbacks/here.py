from datetime import timezone
from loguru import logger
from pydantic_extra_types.pendulum_dt import DateTime
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User
from src.shared.exceptions import (
    GameAlreadyCompleted,
    GameAlreadyStarted,
    RoomNotFound,
    UserNotFound,
)


class HereCallback(Callback):
    """Callback for guessing the action from
    the context when user sends /here command."""

    def process(self, user: User, *, message: types.Message):
        logger.info(f"/here from {user}")
        if self._option_join_just_created_room(user):
            logger.info(f"User {user} joined just created room")
            self.bot.send_message(user.id, "You have joined the room you just created.")
        else:
            logger.info(f"Couldn't determine what to do with /here from {user}")
            self.bot.send_message(
                user.id, "Couldn't determine what to do with the /here command."
            )

    def _option_join_just_created_room(self, user: User) -> bool:
        """
        Context:
            User has just created a room and is not in any room yet.
        Action:
            Join the user to the room they just created.
        """
        if user.room_id is not None:
            logger.debug(f"User {user} is already in a room {user.room_id}")
            return False
        managed_rooms = self.moroz.get_rooms_managed_by_user(user.id)
        active_managed_rooms = [room for room in managed_rooms if room.is_active]
        if not active_managed_rooms:
            logger.debug(f"User {user} does not manage any active rooms")
            return False
        latest_room = max(active_managed_rooms, key=lambda r: r.created_dt)
        # TODO make tz in sqlmodel models timezone aware
        now = DateTime.utcnow()
        created_dt = DateTime.fromisoformat(
            latest_room.created_dt.isoformat()
        ).astimezone(timezone.utc)
        if (now - created_dt).seconds > 60:
            logger.debug(
                f"Latest room {latest_room} for user {user} was created more than 1 minute ago"
            )
            return False
        try:
            self.moroz.join_room_by_short_code(user.id, latest_room.short_code)
        except (
            RoomNotFound,
            UserNotFound,
            GameAlreadyStarted,
            GameAlreadyCompleted,
        ) as e:
            logger.error(f"Failed to join user {user} to room {latest_room}: {e}")
            return False

        return True
