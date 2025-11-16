from itertools import batched

from telebot import types

from src.models.user import User


def get_keyboard(buttons: list[str], *, row_width=1) -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
    for zones_batch in batched(buttons, row_width):
        kb.add(*map(types.KeyboardButton, zones_batch), row_width=row_width)
    return kb


def remove_keyboard() -> types.ReplyKeyboardRemove:
    return types.ReplyKeyboardRemove()


def text(message: types.Message) -> str:
    return message.text if message.text else ""


def user_from_message(message: types.Message) -> User:
    """This function does not return a real User from DB,
    just constructs a User object from message data."""
    return User(
        id=message.from_user.id if message.from_user else 0,
        name=message.chat.first_name,
        username=message.chat.username,
    )
