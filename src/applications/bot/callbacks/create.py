from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User
from src.shared.exceptions import MaxNumberOfRoomsReached


class CreateCallback(Callback):
    """
    Create a new room.

    - show the room code
    - note that the manager is not automatically joined to the room;
      hence, suggest to /join
    """

    def process(self, message: types.Message, user: User):
        logger.info(f"/create from {user}")
        this_user = self.moroz.get_user(user)

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
This room ID: `{room.display_short_code}` \(share this with your friends\)\.
Note that you are not automatically joined to the room; please /join to enter\.""",
            parse_mode="MarkdownV2",
        )
