from unittest.mock import MagicMock

import pytest

from src.models.room import Room
from src.models.user import User
from src.services.moroz import Moroz


@pytest.fixture
def moroz_mock() -> MagicMock:
    return MagicMock(spec=Moroz)


@pytest.fixture
def user_mock() -> User:
    user = MagicMock(spec=User)
    user.__str__ = MagicMock(return_value="this-user")  # type: ignore[method-assign]
    user.name = "Test"
    user.username = "testuser"
    user.id = 12345
    return user


@pytest.fixture
def real_user_factory():
    def _factory(
        id: int = 13579, username: str = "realuser", name: str = "Real"
    ) -> User:
        return User(id=id, username=username, name=name)

    return _factory


@pytest.fixture
def another_user_mock() -> User:
    user = MagicMock(spec=User)
    user.__str__ = MagicMock(return_value="another-user")  # type: ignore[method-assign]
    user.name = "Another"
    user.username = "anotheruser"
    user.id = 654321
    return user


@pytest.fixture
def room_mock() -> Room:
    room = MagicMock(spec=Room)
    room.__str__ = MagicMock(return_value="this-room")  # type: ignore[method-assign]
    room.display_short_code = "1234"
    return room
