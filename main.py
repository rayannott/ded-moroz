from dependency_injector.wiring import Provide, inject

from src.dependencies import ApplicationContainer
from src.services.bot import BotService


@inject
def main(
    bot_service: BotService = Provide[ApplicationContainer.bot_service],
) -> None:
    """Main entry point for the TSO Adapter application."""
    bot_service.run()


if __name__ == "__main__":
    container = ApplicationContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    main()
