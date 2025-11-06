from typing import cast

import dotenv
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from src.applications.bot.app import BotApp
from src.repositories.database import DatabaseRepository
from src.services.moroz import DedMoroz
from src.settings import Settings

dotenv.load_dotenv()


class ApplicationContainer(DeclarativeContainer):
    config = Configuration()
    config.from_pydantic(Settings())  # type: ignore
    config = cast(Settings, config)

    database_repository = Singleton(DatabaseRepository, db_connection=None)

    moroz = Singleton(
        DedMoroz,
        database_repository=database_repository,
        settings=config,
    )

    bot_app = Singleton(BotApp, api_token=config.bot_token, moroz=moroz)
