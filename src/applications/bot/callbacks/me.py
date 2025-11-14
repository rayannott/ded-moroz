from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User


class MeCallback(Callback):
    def process(self, user: User, *, message: types.Message):
        logger.info(f"/me from {user}")
        msg = self.moroz.get_user_information(user)
        self.bot.send_message(user.id, msg)
