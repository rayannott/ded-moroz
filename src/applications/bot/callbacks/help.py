from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User

HELP_MESSAGE = """Welcome to the Moroz Bot!
Something you may want to know to play:
/create, /join yourself using the code (and invite others), /manage to start (among other things) and complete.

Available commands:
/help - show this help message
/start - register yourself with the bot
/join - join an existing room
/name - set or change your display name
/me - show info about yourself (name, username, current room, etc.)
/create - create a new room
/manage - manage room(s) you created (if any): see info, kick players, start/complete game, or delete
/leave - leave the current room (if any)
"""


class HelpCallback(Callback):
    def process(self, user: User, *, message: types.Message):
        logger.info(f"/help from {user}")
        self.bot.send_message(
            user.id,
            HELP_MESSAGE,
        )
