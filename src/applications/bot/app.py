import telebot
from loguru import logger

from src.services.moroz import DedMoroz
from src.applications.bot.callbacks_manager import CallbacksManager


class BotApp:
    def __init__(self, api_token: str, moroz: DedMoroz):
        self.api_token = api_token
        self.moroz = moroz

        self.bot = self.create_bot()
        self.callbacks_manager = CallbacksManager(self.bot, self.moroz)
        self.callbacks_manager.register_callbacks(self.bot)

    def create_bot(self) -> telebot.TeleBot:
        bot = telebot.TeleBot(self.api_token)
        return bot

    def run(self):
        logger.info("Bot started")
        self.bot.polling()
        logger.info("Bot stopped")
