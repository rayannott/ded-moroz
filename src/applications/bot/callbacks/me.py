from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User
from src.shared.exceptions import UserNotFound, RoomNotFound


class MeCallback(Callback):
    """
    Show information about the user.

    - if any, the room the user is currently in
       and the number of participants there
    - the user's custom name (if set by /name)
    - if any, the rooms the user is managing
    """

    def process(self, message: types.Message):
        usr = User.from_message(message)
        logger.info(f"/me from {usr}")
        try:
            this_user = self.moroz.get_user(usr)
        except UserNotFound:
            self.bot.send_message(
                message.chat.id,
                "You are not registered yet. Please /start to register.",
            )
            return
        msg = f"You are {this_user.display_name}"
        if this_user.username is not None:
            msg += f" (@{this_user.username})"
        if this_user.room_id is not None:
            try:
                room = self.moroz.database_repository.get_room(this_user.room_id)
                msg += f"\ncurrently in room {room.short_code:04d}"
                that_room_manager = self.moroz.database_repository.get_user(
                    room.manager_user_id
                )
                msg += f" managed by {that_room_manager.display_name}"
                # TODO show number of participants
            except RoomNotFound:
                logger.error(
                    f"User {this_user} is in {this_user.room_id=}, but the room does not exist"
                )
            except UserNotFound:
                logger.opt(exception=True).error("Manager user not found")
        self.bot.send_message(message.chat.id, msg)
