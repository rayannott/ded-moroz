from abc import ABC, abstractmethod

from telebot import types
import telebot

from src.services.moroz import Moroz


class Callback(ABC):
    def __init__(self, bot: telebot.TeleBot, moroz: Moroz):
        self.bot = bot
        self.moroz = moroz

    @abstractmethod
    def process(self, message: types.Message): ...
