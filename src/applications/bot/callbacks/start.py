from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.shared.exceptions import UserNotFound, UserAlreadyExists
from src.models.user import User


class StartCallback(Callback):
    """Start interaction with the bot.

    - add user to database if not exists."""

    def _create_user(self, message: types.Message):
        new_user = User.from_message(message)
        try:
            self.moroz.create_user(user=new_user)
            self.bot.send_message(
                message.chat.id,
                f"Welcome, {new_user.display_name}! You have been registered.",
            )
        except UserAlreadyExists:
            logger.error(f"User {new_user} already exists when creating.")

    def _greet_again(self, user: User):
        self.bot.send_message(user.id, f"Welcome back, {user.display_name}!")

    def process(self, message: types.Message):
        logger.info(f"/start from {User.from_message(message)}")
        if message.from_user is None:
            return

        try:
            this_user = self.moroz.database_repository.get_user(
                user_id=message.from_user.id
            )
            self._greet_again(this_user)
        except UserNotFound:
            self._create_user(message)
