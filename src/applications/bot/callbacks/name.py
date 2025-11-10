from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User
from src.applications.bot.utils import text


class NameCallback(Callback):
    def process(self, message: types.Message, user: User):
        logger.info(f"/name from {user}")
        self.bot.send_message(
            message.chat.id,
            "Please provide the name you want to use.",
        )
        self.bot.register_next_step_handler(
            message,
            self._set_name,
            user=user,
        )

    def _set_name(self, message: types.Message, user: User):
        new_name = text(message).strip()
        logger.debug(f"Setting name for {user} to {new_name!r}")

        self.moroz.update_name(user, new_name)

        self.bot.send_message(
            message.chat.id,
            f"Your name has been set to '{new_name}'.",
        )
        logger.debug(f"Name for {user} set to {new_name!r}")
