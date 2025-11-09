from abc import ABC, abstractmethod

import telebot
from telebot import types

from src.models.room import Room
from src.models.user import User
from src.services.moroz import Moroz


class ManagementCallback(ABC):
    def __init__(self, bot: telebot.TeleBot, moroz: Moroz):
        self.bot = bot
        self.moroz = moroz

    @abstractmethod
    def process_management(self, message: types.Message, user: User, room: Room): ...
