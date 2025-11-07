from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.applications.bot.utils import get_keyboard, remove_keyboard, text
from src.models.user import User


class KickCallback(Callback):
    """
    Kick a user from one of the rooms the caller is managing.

    - show keyboard of the (unfinished) rooms that this user managing
    """

    def process(self, message: types.Message):
        logger.info(f"/kick from {User.from_message(message)}")
        kb = get_keyboard(["one", "two"])
        msg = self.bot.send_message(message.chat.id, "Room creation.", reply_markup=kb)
        self.bot.register_next_step_handler(msg, self._next_step)

    def _next_step(self, message: types.Message):
        option = text(message)
