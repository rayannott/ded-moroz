import telebot
from loguru import logger
from telebot import types

from src.applications.bot.callbacks.echo import EchoCallback
from src.applications.bot.callbacks.help import HelpCallback
from src.applications.bot.callbacks.start import StartCallback
from src.services.moroz import DedMoroz


class CallbacksManager:
    """Manages bot callbacks."""

    def __init__(self, bot: telebot.TeleBot, ded_moroz: DedMoroz):
        logger.debug("Initializing CallbacksManager")
        self.bot = bot
        self.ded_moroz = ded_moroz

    def register_callbacks(self, bot: telebot.TeleBot):
        @bot.message_handler(commands=["start"])
        def start_handler(message: types.Message):
            StartCallback(self.bot, self.ded_moroz).process(message)

        @bot.message_handler(commands=["help"])
        def help_handler(message: types.Message):
            HelpCallback(self.bot, self.ded_moroz).process(message)

        # @bot.message_handler(commands=["name"])
        # def name_handler(message: types.Message):
        #     bot.reply_to(message, "Setting a name is not implemented yet.")

        # @bot.message_handler(commands=["create"])
        # def create_handler(message: types.Message):
        #     bot.reply_to(message, "Room creation is not implemented yet.")

        # @bot.message_handler(commands=["join"])
        # def join_handler(message: types.Message):
        #     bot.reply_to(message, "Room joining is not implemented yet.")

        @bot.message_handler(func=lambda message: True)
        def echo_handler(message: types.Message):
            EchoCallback(self.bot, self.ded_moroz).process(message)
