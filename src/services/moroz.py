from src.repositories.database import DatabaseRepository


class DedMoroz:
    """The main game logic."""

    def __init__(self, database_repository: DatabaseRepository):
        self.database_repository = database_repository
