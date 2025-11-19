import telebot
from loguru import logger

from src.applications.bot.callbacks_manager import CallbacksManager
from src.services.moroz import Moroz


class BotApp:
    def __init__(self, api_token: str, moroz: Moroz):
        self.api_token = api_token
        self.moroz = moroz

        self.bot = telebot.TeleBot(self.api_token)
        self.callbacks_manager = CallbacksManager(self.bot, self.moroz)
        self.callbacks_manager.register_callbacks(self.bot)

    def run(self):
        logger.info("Bot started")
        self.bot.infinity_polling()
        logger.info("Bot stopped")
