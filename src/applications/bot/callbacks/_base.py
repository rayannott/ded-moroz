from abc import ABC, abstractmethod

from telebot import types
import telebot

from src.services.moroz import DedMoroz


class Callback(ABC):
    def __init__(self, bot: telebot.TeleBot, ded_moroz: DedMoroz):
        self.bot = bot
        self.ded_moroz = ded_moroz

    @abstractmethod
    def do(self, message: types.Message): ...
