from telebot import types
from loguru import logger

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class HelpCallback(Callback):
    def process(self, message: types.Message):
        logger.info(f"/help from {User.from_message(message)}")
        self.bot.reply_to(
            message,
            "This is the help message. Available commands: /start, /help, /name, /create, /leave, /me, /join.",
        )
