from loguru import logger
from telebot import types

from src.applications.bot.callbacks._base import Callback
from src.models.user import User
from src.applications.bot.utils import get_keyboard, remove_keyboard


def text(message: types.Message) -> str:
    return message.text if message.text else ""


class CreateCallback(Callback):
    """
    Create a new room.

    - show the room code
    - note that the manager is not automatically joined to the room;
      hence, suggest to /join
    """

    def process(self, message: types.Message):
        logger.info(f"/create from {User.from_message(message)}")
        kb = get_keyboard(["one", "two"])
        msg = self.bot.send_message(message.chat.id, "Room creation.", reply_markup=kb)
        self.bot.register_next_step_handler(msg, self._next_step)

    def _next_step(self, message: types.Message):
        option = text(message)
        msg = f"{option!r} room creation selected. Code: `XXXX`"
        self.bot.send_message(
            message.chat.id,
            msg,
            reply_markup=remove_keyboard(),
        )
