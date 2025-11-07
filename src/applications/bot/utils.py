from itertools import batched

from telebot import types


def get_keyboard(buttons: list[str]) -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for zones_batch in batched(buttons, 2):
        kb.add(*map(types.KeyboardButton, zones_batch), row_width=1)
    return kb


def remove_keyboard() -> types.ReplyKeyboardRemove:
    return types.ReplyKeyboardRemove()
