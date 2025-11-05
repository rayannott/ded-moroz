from src.models.room import Room
from pydantic_extra_types.pendulum_dt import DateTime


class DatabaseRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_room(self, room_name: str) -> Room:
        room = Room(
            code=1234,
            name=room_name,
            created_dt=DateTime.utcnow(),
        )
        # TODO populate the database
        return room

    def get_room(self, room_id: int) -> Room | None:
        # TODO implement database retrieval
        return None
