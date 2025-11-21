import telebot
from loguru import logger

from src.applications.bot.callbacks_manager import CallbacksManager
from src.applications.bot.utils import get_git_info
from src.services.moroz import Moroz


class BotApp:
    def __init__(self, api_token: str, moroz: Moroz):
        self.api_token = api_token
        self.moroz = moroz

        self.bot = telebot.TeleBot(self.api_token)
        self.callbacks_manager = CallbacksManager(self.bot, self.moroz)
        self.callbacks_manager.register_callbacks(self.bot)

    def _notify_admin_with(self, message: str):
        if self.moroz.admin_user_id is not None:
            self.bot.send_message(
                self.moroz.admin_user_id,
                message,
            )

    def run(self):
        logger.info("Bot started")
        _git = get_git_info()
        self._notify_admin_with(
            f"Bot has just started.\n\n{_git}" if _git else "Bot has just started."
        )

        self.bot.infinity_polling()

        logger.info("Bot stopped")
        self._notify_admin_with("Bot has just stopped.")
