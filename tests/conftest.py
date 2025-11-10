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
    return MagicMock(spec=User)


@pytest.fixture
def room_mock() -> Room:
    return MagicMock(spec=Room)
