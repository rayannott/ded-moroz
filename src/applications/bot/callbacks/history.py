from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User


class HistoryCallback(Callback):
    def process(self, user: User, *, message: types.Message):
        logger.info(f"/history from {user}")
        self.bot.send_message(
            user.id,
            "History lookup is not implemented yet, "
            "but feel free to help out by contributing at "
            "https://github.com/rayannott/ded-moroz/issues/26",
        )
