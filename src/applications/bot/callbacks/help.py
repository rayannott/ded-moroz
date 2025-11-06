from telebot import types

from src.applications.bot.callbacks._base import Callback


class HelpCallback(Callback):
    def do(self, message: types.Message):
        self.bot.reply_to(
            message,
            "This is the help message. Available commands: /start, /help, /name, /create, /join.",
        )
