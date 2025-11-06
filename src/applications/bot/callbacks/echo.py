from telebot import types

from src.applications.bot.callbacks._base import Callback


class EchoCallback(Callback):
    def do(self, message: types.Message):
        self.bot.reply_to(message, f"Unknown command: {message.text}")
