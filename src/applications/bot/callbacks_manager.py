import telebot
from loguru import logger
from telebot import types

from src.applications.bot.callbacks.create import CreateCallback
from src.applications.bot.callbacks.echo import EchoCallback
from src.applications.bot.callbacks.help import HelpCallback
from src.applications.bot.callbacks.join import JoinCallback
from src.applications.bot.callbacks.leave import LeaveCallback
from src.applications.bot.callbacks.me import MeCallback
from src.applications.bot.callbacks.name import NameCallback
from src.applications.bot.callbacks.start import StartCallback
from src.applications.bot.callbacks.management.manage import ManageCallback
from src.applications.bot.callbacks.easter import EasterCallback
from src.services.moroz import Moroz


class CallbacksManager:
    """Manages bot callbacks."""

    def __init__(self, bot: telebot.TeleBot, moroz: Moroz):
        logger.debug("Initializing CallbacksManager")
        self.bot = bot
        self.moroz = moroz

    def register_callbacks(self, bot: telebot.TeleBot):
        # TODO maybe make callbacks just functions?
        @bot.message_handler(commands=["start"])
        def start_handler(message: types.Message):
            StartCallback(self.bot, self.moroz).process(message)

        @bot.message_handler(commands=["help"])
        def help_handler(message: types.Message):
            HelpCallback(self.bot, self.moroz).process(message)

        @bot.message_handler(commands=["me"])
        def me_handler(message: types.Message):
            MeCallback(self.bot, self.moroz).process(message)

        @bot.message_handler(commands=["leave"])
        def leave_handler(message: types.Message):
            LeaveCallback(self.bot, self.moroz).process(message)

        @bot.message_handler(commands=["join"])
        def join_handler(message: types.Message):
            JoinCallback(self.bot, self.moroz).process(message)

        @bot.message_handler(commands=["manage"])
        def manage_handler(message: types.Message):
            ManageCallback(self.bot, self.moroz).process(message)

        @bot.message_handler(commands=["create"])
        def create_handler(message: types.Message):
            CreateCallback(self.bot, self.moroz).process(message)

        @bot.message_handler(commands=["name"])
        def name_handler(message: types.Message):
            NameCallback(self.bot, self.moroz).process(message)

        @bot.message_handler(commands=["easter"])
        def easter_handler(message: types.Message):
            EasterCallback(self.bot, self.moroz).process(message)

        @bot.message_handler(func=lambda message: True)
        def echo_handler(message: types.Message):
            EchoCallback(self.bot, self.moroz).process(message)
