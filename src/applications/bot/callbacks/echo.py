from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User


class EchoCallback(Callback):
    def process(self, user: User, *, message: types.Message):
        logger.info(f"/echo from {user}")
        self.bot.reply_to(message, f"Unknown command {message.text!r}. Try /help.")
