from pathlib import Path

import yaml

LOCALIZATION_FILE = Path(__file__).parent / "loc.yaml"

type NestedDict = dict[str, NestedDict]


class Locale:
    """A class to manage localization settings.

    Example usage:
    >>> Locale("en")("start.new-user")
    'Welcome, new user!'
    >>> Locale("ru")("start.new-user")
    'Добро пожаловать!'

    Example loc.yaml structure:
    start:
        welcome:
            en:  Welcome to the bot!
            ru:  Добро пожаловать в бота!
        welcome-back:
            en: Welcome back, {username}!
            ru: С возвращением, {username}!
    """

    _cache: NestedDict | None = None

    @classmethod
    def load_data(cls):
        if cls._cache is None:
            with open(LOCALIZATION_FILE, "r", encoding="utf-8") as f:
                cls._cache = yaml.safe_load(f)
            assert cls._cache is not None
        return cls._cache

    def __init__(self, lang: str):
        self.lang = lang
        self.raw_data = self.load_data()

    def __call__(self, key: str) -> str:
        # parts = key.split(".")
        # TODO(locale)
        return key
