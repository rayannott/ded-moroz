from dependency_injector.wiring import Provide, inject

from src.dependencies import ApplicationContainer
from src.applications.bot.app import BotApp


@inject
def main(
    bot_app: BotApp = Provide[ApplicationContainer.bot_app],
) -> None:
    """Main entry point for the TSO Adapter application."""
    bot_app.run()


if __name__ == "__main__":
    container = ApplicationContainer()
    container.wire(modules=[__name__])
    main()
