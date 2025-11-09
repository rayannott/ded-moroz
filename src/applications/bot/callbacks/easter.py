from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class EasterCallback(Callback):
    def process(self, message: types.Message):
        logger.info(f"/easter from {User.from_message(message)}")
        