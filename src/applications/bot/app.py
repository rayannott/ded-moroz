import telebot
from loguru import logger

from src.services.moroz import DedMoroz
from src.applications.bot.callbacks_manager import CallbacksManager


class BotApp:
    def __init__(self, api_token: str, ded_moroz: DedMoroz):
        self.api_token = api_token
        self.ded_moroz = ded_moroz

        self.bot = self.create_bot()
        self.callbacks_manager = CallbacksManager(self.bot, self.ded_moroz)
        self.callbacks_manager.register_callbacks(self.bot)

    def create_bot(self) -> telebot.TeleBot:
        bot = telebot.TeleBot(self.api_token)
        return bot

    def run(self):
        logger.info("Bot started")
        self.bot.polling()
        logger.info("Bot stopped")
