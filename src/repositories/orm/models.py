from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
)

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(tz=ZoneInfo("UTC"))


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    name: Mapped[str | None] = mapped_column(nullable=True)
    room_id: Mapped[str | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)


class RoomORM(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(primary_key=True)
    short_code: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    manager_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_dt: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
