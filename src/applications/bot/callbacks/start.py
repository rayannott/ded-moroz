from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.applications.bot.utils import user_from_message
from src.models.user import User
from src.shared.exceptions import UserNotFound


class StartCallback(Callback):
    def process_wrap(self, message: types.Message):
        # overriding to NOT check user existence beforehand
        # since the point of /start is to create user if not exists
        return self.process(user_from_message(message), message=message)

    def _create_user(self, user: User) -> User:
        new_user = self.moroz.create_user(user)
        self.bot.send_message(
            new_user.id,
            f"Welcome, {new_user.display_name}! You have been registered.",
        )
        return new_user

    def _greet_again(self, user: User):
        self.bot.send_message(user.id, f"Welcome back, {user.display_name}!")

    def process(self, user: User, *, message: types.Message):
        logger.info(f"/start from {user}")

        try:
            this_user = self.moroz.get_user(user)
            self._greet_again(this_user)
        except UserNotFound:
            this_user = self._create_user(user)

        assert message.from_user is not None
        self._update_locale(this_user, message.from_user.language_code or "en")

    def _update_locale(self, user: User, locale_code: str):
        # TODO(locale): implement actual locale updating
        pass
