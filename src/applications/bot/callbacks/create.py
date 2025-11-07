from loguru import logger
from telebot import types
from telebot.formatting import escape_markdown

from src.applications.bot.callbacks._base import Callback
from src.applications.bot.utils import text
from src.models.user import User
from src.shared.exceptions import MaxNumberOfRoomsReached, UserNotFound


class CreateCallback(Callback):
    """
    Create a new room.

    - show the room code
    - note that the manager is not automatically joined to the room;
      hence, suggest to /join
    """

    def process(self, message: types.Message):
        usr = User.from_message(message)
        logger.info(f"/create from {usr}")

        try:
            this_user = self.moroz.get_user(usr)
        except UserNotFound:
            self.bot.send_message(
                message.chat.id,
                "You are not registered yet. Please /start to register.",
            )
            return

        try:
            room = self.moroz.create_room(
                created_by_user_id=this_user.id,
                room_name="New Room",
            )
        except MaxNumberOfRoomsReached:
            self.bot.send_message(
                message.chat.id,
                "You have reached the maximum number of rooms you can create. "
                "Please /delete an existing room before creating a new one.",
            )
            return

        self.bot.send_message(
            message.chat.id,
            rf"""Room created successfully\! 🎉
This room ID: `{room.short_code:04d}` \(share this with your friends\)\.
Note that you are not automatically joined to the room; please /join to enter\.""",
            parse_mode="MarkdownV2",
        )
