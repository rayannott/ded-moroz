from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class StartCallback(Callback):
    def process(self, message: types.Message):
        logger.info(f"/start from {User.from_message(message)}")
        self.bot.send_message(message.chat.id, "Hello! Try /help.")
