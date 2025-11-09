from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User
from src.models.room import Room
from src.applications.bot.utils import get_keyboard, text, remove_keyboard
from src.shared.exceptions import RoomNotFound, UserNotFound, NotInRoom


_CANCEL_TEXT = "Cancel"


class DeleteCallback(Callback):
    """
    Delete one of the rooms managed by the user.

    - show keyboard of the (unfinished) rooms that this user managing
    """

    def process(self, message: types.Message):
        usr = User.from_message(message)
        logger.info(f"/delete from {usr}")
        try:
            managed_rooms = self.moroz.get_active_rooms_managed_by_user(usr)
        except UserNotFound:
            self.bot.send_message(
                message.chat.id,
                "You are not registered yet. Please /start to register.",
            )
            return
        
        if not managed_rooms:
            self.bot.send_message(
                message.chat.id,
                "You are not managing any active rooms currently.",
            )
            return

        code_to_room = {room.short_code: room for room in managed_rooms}

        # TODO add showing how many players are in each room

        answer = self.bot.send_message(
            message.chat.id,
            "Please select a room to delete:",
            reply_markup=get_keyboard(
                [f"{room.short_code:04d}" for room in managed_rooms] + [_CANCEL_TEXT]
            ),
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
        chosen_text = text(message)
        if chosen_text == _CANCEL_TEXT:
            self.bot.send_message(
                message.chat.id,
                "Room deletion cancelled.",
                reply_markup=remove_keyboard(),
            )
            logger.info(f"Room deletion cancelled by {user}")
            return
        room_short_code = int(chosen_text)
        logger.info(f"Room to delete chosen: {room_short_code} by {user}")

        room = code_to_room.get(room_short_code)
        if room is None:
            logger.critical(f"Room {room_short_code=} not found; {user=}")
            self.bot.send_message(
                message.chat.id, "Internal error.", reply_markup=remove_keyboard()
            )
            return

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

        self._cleanup_after_room_deletion(room, users_in_room)

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

    def _cleanup_after_room_deletion(self, room: Room, users_in_room: list[User]):
        logger.info(
            f"Cleaning up after deletion of {room.id=} with {len(users_in_room)} players"
        )
        for user in users_in_room:
            if self._clenup_one_user(user):
                self._notify_one_user(user, room)
