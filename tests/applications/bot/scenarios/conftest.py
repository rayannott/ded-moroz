import pytest
from sqlmodel import create_engine

from src.repositories.database import DatabaseRepository
from src.services.moroz import Moroz


@pytest.fixture(scope="function")
def database_repo():
    # Use a fresh in-memory DB for each test
    engine = create_engine("sqlite:///:memory:", echo=False)
    repo = DatabaseRepository(engine)
    yield repo
    engine.dispose()


@pytest.fixture(scope="function")
def moroz_integrated(database_repo):
    # Create the main application logic object
    app = Moroz(
        database_repository=database_repo,
        max_rooms_managed_by_user=2,
        min_players_to_start_game=3,
    )
    return app
