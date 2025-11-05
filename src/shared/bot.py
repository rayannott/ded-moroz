import os

import dotenv
import telebot
from telebot import types

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
assert BOT_TOKEN is not None


def create_bot(api_token: str) -> telebot.TeleBot:
    bot = telebot.TeleBot(api_token)

    @bot.message_handler(commands=["start"])
    def start_handler(message: types.Message):
        bot.reply_to(message, "Hello!")

    @bot.message_handler(commands=["help"])
    def help_handler(message: types.Message):
        bot.reply_to(
            message,
            "Here are some commands you can use:\n"
            "/start - Start the conversation\n"
            "/help - Get help",
        )

    @bot.message_handler(commands=["name"])
    def name_handler(message: types.Message):
        bot.reply_to(message, "Setting a name is not implemented yet.")

    @bot.message_handler(commands=["create"])
    def create_handler(message: types.Message):
        bot.reply_to(message, "Room creation is not implemented yet.")

    @bot.message_handler(commands=["join"])
    def join_handler(message: types.Message):
        bot.reply_to(message, "Room joining is not implemented yet.")

    @bot.message_handler(func=lambda message: True)
    def echo_handler(message: types.Message):
        bot.reply_to(message, f"Unknown command: {message.text}")

    return bot
