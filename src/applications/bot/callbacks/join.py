from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User


class JoinCallback(Callback):
    """
    Join a room by room code.
    
    show how the user will be displayed to others in the room
    and ask to set /name if their name is potentially unclear
    """
    def process(self, message: types.Message):
        logger.info(f"/join from {User.from_message(message)}")
        self.bot.send_message(message.chat.id, "Welcome! You have joined the chat.")
