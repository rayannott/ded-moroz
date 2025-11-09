from telebot import types
from loguru import logger

from src.applications.bot.callbacks.base import Callback
from src.models.user import User


HELP_MESSAGE = """ Play secret santa with your friends!
Available commands:
help - show this help message
start - get started with the bot
join - join a room
name - set a display name
me - show info about yourself
create - create a new room
manage - manage your rooms (start/delete games)
leave - leave the current room
"""


class HelpCallback(Callback):
    def process(self, message: types.Message, user: User):
        logger.info(f"/help from {user}")
        self.bot.send_message(
            message.chat.id,
            HELP_MESSAGE,
        )
