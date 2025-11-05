import telebot
from loguru import logger


class BotService:
    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot

    def run(self):
        logger.info("Bot started")
        self.bot.polling()
        logger.info("Bot stopped")
