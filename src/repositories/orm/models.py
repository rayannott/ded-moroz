from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, ForeignKey, Integer
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
    joined_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    username: Mapped[str | None] = mapped_column(nullable=True)
    name: Mapped[str | None] = mapped_column(nullable=True)
    room_id: Mapped[str | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)

    def __repr__(self) -> str:
        return (
            f"UserORM(id={self.id!r}, joined_dt={self.joined_dt!r}, "
            f"username={self.username!r}, name={self.name!r}, room_id={self.room_id!r})"
        )


class RoomORM(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(primary_key=True)
    short_code: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    manager_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_dt: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"RoomORM(id={self.id!r}, short_code={self.short_code!r}, name={self.name!r}, "
            f"manager_user_id={self.manager_user_id!r}, created_dt={self.created_dt!r}, "
            f"started_at={self.started_at!r}, completed_dt={self.completed_dt!r})"
        )


class TargetORM(Base):
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    target_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        return (
            f"TargetORM(id={self.id!r}, room_id={self.room_id!r}, "
            f"user_id={self.user_id!r}, target_user_id={self.target_user_id!r})"
        )
