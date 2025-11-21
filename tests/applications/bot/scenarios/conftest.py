import pytest
from sqlmodel import create_engine

from src.models.room import Room
from src.models.user import User
from src.repositories.database import DatabaseRepository
from src.services.moroz import Moroz


@pytest.fixture(scope="function")
def database_repo():
    engine = create_engine("sqlite:///:memory:", echo=False)
    repo = DatabaseRepository(engine)
    yield repo
    engine.dispose()


@pytest.fixture(scope="function")
def moroz_integrated(database_repo):
    app = Moroz(
        database_repository=database_repo,
        max_rooms_managed_by_user=2,
        min_players_to_start_game=3,
    )
    return app


@pytest.fixture
def create_manager_room(database_repo: DatabaseRepository) -> tuple[User, Room]:
    manager = database_repo.create_user(id=401, username="manager", name="Manager")
    room = database_repo.create_room(created_by_user_id=manager.id)
    manager = database_repo.get_user(manager.id)
    room = database_repo.get_room(room.id)
    return manager, room
