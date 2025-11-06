from src.models.room import Room
from pydantic_extra_types.pendulum_dt import DateTime


class DatabaseRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_room(self, created_by_user_id: int, room_name: str) -> Room:
        room = Room(
            code=1234,
            name=room_name,
            manager_user_id=created_by_user_id,
            created_dt=DateTime.utcnow(),
        )
        # TODO populate the database
        return room

    def get_room(self, room_id: int) -> Room | None:
        return None

    def join_room(self, user_id: int, room_id: int) -> bool:
        return True

    def leave_room(self, user_id: int, room_id: int) -> bool:
        return True

    def set_user_name(self, user_id: int, name: str) -> bool:
        return True
