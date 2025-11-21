from loguru import logger
from telebot import types

from src.applications.bot.callbacks.base import Callback
from src.models.user import User

HELP_MESSAGE = """Welcome to the Secret Santa Bot!
To start with,
/create a room,
/join using the four-digit code (and invite others),
/manage to start (among other things).

Available commands:
/help - show this help message
/start - register yourself with the bot
/join - join an existing room
/name - set or change your display name
/me - show info about yourself (name, username, current room, etc.)
/create - create a new room
/manage - manage room(s) you created (if any): see info, kick players, start/complete game, or delete
/leave - leave the current room (if any){admin_info}
"""


class HelpCallback(Callback):
    def process(self, user: User, *, message: types.Message):
        logger.info(f"/help from {user}")
        _admin_contact = (
            f"{self.moroz.admin_name} (@{self.moroz.admin_username})"
            if self.moroz.admin_name and self.moroz.admin_username
            else (f"@{self.moroz.admin_username}" if self.moroz.admin_username else "")
        )
        self.bot.send_message(
            user.id,
            HELP_MESSAGE.format(
                admin_info=(
                    f"\n\nFeel free to share feedback with me: {_admin_contact}."
                    if _admin_contact
                    else ""
                ),
            ),
        )
