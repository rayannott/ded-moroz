import subprocess
from itertools import batched
from typing import NamedTuple

from loguru import logger
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
        id=message.chat.id,
        name=message.chat.first_name,
        username=message.chat.username,
    )


class GitInfo(NamedTuple):
    branch_name: str
    commit_hash: str
    commit_message: str

    def __str__(self) -> str:
        return (
            f"Branch: {self.branch_name}\n"
            f"Commit: {self.commit_hash}\n"
            f"Message: {self.commit_message}"
        )


def get_git_info() -> GitInfo | None:
    def _output(cmd: list[str]) -> str:
        return (
            subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
            )
            .decode("utf-8")
            .strip()
        )

    try:
        commit_hash = _output(["git", "rev-parse", "--short", "HEAD"])
        branch_name = _output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        commit_message = _output(["git", "log", "-1", "--pretty=%B"])
        return GitInfo(
            branch_name=branch_name,
            commit_hash=commit_hash,
            commit_message=commit_message,
        )
    except Exception as e:
        logger.warning(f"Failed to get git info: {e}")
        return None
