from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User
from src.shared.exceptions import UserNotFound
from src.applications.bot.utils import text


class NameCallback(Callback):
    """
    Set the name of the user,
    overriding `message.chat.first_name`.
    """

    def process(self, message: types.Message):
        usr = User.from_message(message)
        logger.info(f"/name from {usr}")

        try:
            this_user = self.moroz.get_user(usr)
        except UserNotFound:
            self.bot.send_message(
                message.chat.id,
                "You are not registered yet. Please /start to register.",
            )
            return

        self.bot.send_message(
            message.chat.id,
            "Please provide the name you want to use.",
        )
        self.bot.register_next_step_handler(
            message,
            self._set_name,
            user=this_user,
        )

    def _set_name(self, message: types.Message, user: User):
        new_name = text(message).strip()
        logger.info(f"Setting name for {user} to {new_name!r}")

        self.moroz.update_name(user, new_name)

        self.bot.send_message(
            message.chat.id,
            f"Your name has been set to '{new_name}'.",
        )
        logger.info(f"Name for {user} set to {new_name!r}")
