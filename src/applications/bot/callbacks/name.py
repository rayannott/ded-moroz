from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.applications.bot.utils import text
from src.models.user import User
from src.shared.exceptions import InvalidName


class NameCallback(Callback):
    def process(self, user: User, *, message: types.Message):
        logger.info(f"/name from {user}")
        name_provided_msg = self.bot.send_message(
            user.id,
            "Please provide the name you want to use.",
        )
        self.bot.register_next_step_handler(
            name_provided_msg,
            self._set_name,
            user=user,
        )

    def _set_name(self, message: types.Message, user: User):
        new_name = text(message).strip()
        logger.debug(f"Setting name for {user} to {new_name!r}")

        try:
            self.moroz.update_name(user, new_name)
        except InvalidName as e:
            self.bot.send_message(
                user.id,
                f"Invalid name: {e}. Please try again with a different name.",
            )
            return

        self.bot.send_message(
            user.id,
            f"Your name has been set to {new_name!r}.",
        )
        logger.debug(f"Name for {user} set to {new_name!r}")
