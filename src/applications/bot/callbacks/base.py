from abc import ABC, abstractmethod

import telebot
from loguru import logger
from telebot import types

from src.models.user import User
from src.services.moroz import Moroz
from src.shared.exceptions import UserNotFound
from src.applications.bot.utils import user_from_message


class Callback(ABC):
    def __init__(self, bot: telebot.TeleBot, moroz: Moroz):
        self.bot = bot
        self.moroz = moroz

    def process_wrap(self, message: types.Message):
        """Wrapper to process message with user lookup and error handling.
        Override if user existence is not required."""
        if message.from_user is None:
            logger.warning(f"Message {message} has no from_user; cannot identify user.")
            return
        if message.from_user.is_bot:
            logger.info(f"Ignoring message from bot user {message.from_user}")
            return

        usr = user_from_message(message)

        try:
            user_actual = self.moroz.get_user(usr)
            logger.info(f"{self.__class__.__name__} from {user_actual}: {message.text}")
            return self.process(message, user=user_actual)
        except UserNotFound:
            self.bot.send_message(
                message.chat.id,
                "You are not registered yet. Please /start to register.",
            )
            logger.info(f"User {usr} is not registered.")
            return

    @abstractmethod
    def process(self, message: types.Message, user: User): ...
