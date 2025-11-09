from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User


class EasterCallback(Callback):
    def process(self, message: types.Message, user: User):
        logger.info(f"/easter from {user}")
