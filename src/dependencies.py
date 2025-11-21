from typing import cast

import dotenv
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton
from sqlalchemy import create_engine

from src.applications.bot.app import BotApp
from src.repositories.database import DatabaseRepository
from src.services.moroz import Moroz
from src.settings import Settings

dotenv.load_dotenv()


class ApplicationContainer(DeclarativeContainer):
    config = Configuration()
    config.from_pydantic(Settings())  # type: ignore
    config = cast(Settings, config)  # type: ignore[assignment]

    db_engine = Singleton(create_engine, config.database_url)

    database_repository = Singleton(DatabaseRepository, engine=db_engine)

    moroz = Singleton(
        Moroz,
        database_repository=database_repository,
        max_rooms_managed_by_user=config.max_rooms_managed_by_user,
        min_players_to_start_game=config.min_players_to_start_game,
        admin_name=config.admin_name,
        admin_username=config.admin_username,
        admin_user_id=config.admin_user_id,
    )

    bot_app = Singleton(BotApp, api_token=config.bot_token, moroz=moroz)
