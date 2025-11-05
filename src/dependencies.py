from typing import cast

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from src.shared.bot import create_bot
from src.services.bot import BotService
from src.settings import Settings


class ApplicationContainer(DeclarativeContainer):
    config = Configuration()
    config.from_pydantic(Settings())  # type: ignore
    config = cast(Settings, config)

    bot = Singleton(create_bot, api_token=config.bot_token)

    bot_service = Singleton(BotService, bot=bot)
