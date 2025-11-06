from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class EchoCallback(Callback):
    def process(self, message: types.Message):
        logger.info(f"/echo from {User.from_message(message)}")
        self.bot.reply_to(message, f"Unknown command '{message.text}'. Try /help.")
