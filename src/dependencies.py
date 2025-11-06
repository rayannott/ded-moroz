from typing import cast

import dotenv
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from src.applications.bot.app import BotApp
from src.services.moroz import DedMoroz
from src.settings import Settings

dotenv.load_dotenv()


class ApplicationContainer(DeclarativeContainer):
    config = Configuration()
    config.from_pydantic(Settings())  # type: ignore
    config = cast(Settings, config)

    ded_moroz = Singleton(DedMoroz)

    bot_app = Singleton(BotApp, api_token=config.bot_token, ded_moroz=ded_moroz)
