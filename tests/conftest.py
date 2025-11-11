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
    user.id = 123456
    return user


@pytest.fixture
def room_mock() -> Room:
    room = MagicMock(spec=Room)
    room.__str__ = MagicMock(return_value="this-room")  # type: ignore[method-assign]
    room.display_short_code = "1234"
    return room
