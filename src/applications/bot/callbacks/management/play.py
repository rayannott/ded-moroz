import telebot
from telebot import types

from src.models.room import Room
from src.models.user import User
from src.services.moroz import Moroz


def play(
    bot: telebot.TeleBot, moroz: Moroz, message: types.Message, room: Room, user: User
):
    pass
