from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User
from src.models.room import Room
from src.applications.bot.utils import get_keyboard, text, remove_keyboard
from src.shared.exceptions import RoomNotFound, UserNotFound


class DeleteCallback(Callback):
    """
    Delete one of the rooms managed by the user.

    - show keyboard of the (unfinished) rooms that this user managing
    """

    def process(self, message: types.Message):
        usr = User.from_message(message)
        logger.info(f"/delete from {usr}")

        managed_rooms = self.moroz.get_rooms_managed_by_user(usr)
        if not managed_rooms:
            self.bot.send_message(
                message.chat.id,
                "You are not managing any rooms currently.",
            )
            return

        code_to_room = {room.short_code: room for room in managed_rooms}

        # TODO add showing how many players are in each room

        answer = self.bot.send_message(
            message.chat.id,
            "Please select a room to delete:",
            reply_markup=get_keyboard([f"{room.short_code:04d}" for room in managed_rooms]),
        )
        self.bot.register_next_step_handler(
            answer,
            self._handle_room_chosen,
            user=usr,
            code_to_room=code_to_room,
        )

    def _handle_room_chosen(
        self,
        message: types.Message,
        user: User,
        code_to_room: dict[int, Room],
    ):
        room_short_code = int(text(message))
        logger.info(f"Room to delete chosen: {room_short_code} by {user}")

        room = code_to_room.get(room_short_code)
        if room is None:
            logger.critical(f"Room {room_short_code=} not found; {user=}")
            self.bot.send_message(
                message.chat.id, "Internal error.", reply_markup=remove_keyboard()
            )
            return

        try:
            self.moroz.delete_room(
                user=user,
                room_id=room.id,
            )
        except (RoomNotFound, UserNotFound):
            logger.opt(exception=True).error(
                f"Error deleting room id={room.id} by user {user}"
            )
            self.bot.send_message(
                message.chat.id, "Internal error.", reply_markup=remove_keyboard()
            )
            return

        self.bot.send_message(
            message.chat.id,
            f"Room {room.short_code:04d} deleted successfully. 🎉",
            reply_markup=remove_keyboard(),
        )
