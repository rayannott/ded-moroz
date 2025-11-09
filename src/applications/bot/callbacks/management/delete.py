from telebot import types
import telebot

from src.services.moroz import Moroz
from loguru import logger
from src.models.room import Room
from src.models.user import User
from src.shared.exceptions import UserNotFound, RoomNotFound, NotInRoom
from src.applications.bot.utils import remove_keyboard


def delete(
    bot: telebot.TeleBot, moroz: Moroz, message: types.Message, room: Room, user: User
):
    try:
        users_in_room = moroz.database_repository.get_users_in_room(room.id)
        moroz.delete_room(
            room_id=room.id,
        )
    except RoomNotFound:
        logger.opt(exception=True).error(f"Error deleting {room.id=} by user {user}")
        bot.send_message(
            message.chat.id, "Internal error.", reply_markup=remove_keyboard()
        )
        return

    bot.send_message(
        message.chat.id,
        f"Room {room.short_code:04d} ({len(users_in_room)} players) deleted successfully. 🎉",
        reply_markup=remove_keyboard(),
    )
    logger.info(f"Room {room} deleted by {user}")

    _cleanup_after_room_deletion(bot, moroz, room, user, users_in_room)


def _clenup_one_user(moroz: Moroz, user: User) -> bool:
    logger.debug(f"Cleaning up user {user} after room deletion")
    try:
        this_user = moroz.get_user(user)
    except UserNotFound:
        logger.opt(exception=True).error(
            f"Error cleaning up user {user} after room deletion"
        )
        return False

    logger.debug(f"Removing user {this_user} from room id={this_user.room_id}")
    try:
        moroz.leave_room(
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


def _notify_one_user(bot: telebot.TeleBot, user: User, ex_room: Room):
    logger.debug(f"Notifying user {user} about {ex_room} deletion")
    bot.send_message(
        user.id,
        f"The room {ex_room.short_code:04d} you were in has been deleted by its manager. You have been removed from the room.",
    )


def _cleanup_after_room_deletion(
    bot: telebot.TeleBot,
    moroz: Moroz,
    room: Room,
    user: User,
    users_in_room: list[User],
):
    logger.info(
        f"Cleaning up after deletion of {room.id=} with {len(users_in_room)} players"
    )
    for user in users_in_room:
        if _clenup_one_user(moroz, user):
            _notify_one_user(bot, user, room)
