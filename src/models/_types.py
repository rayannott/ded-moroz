from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.types import DateTime, TypeDecorator


class UTCDateTime(TypeDecorator):
    """
    Store all datetimes as naive UTC in the DB.
    Always return timezone-aware UTC datetimes in Python.
    """

    impl = DateTime
    cache_ok = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("timezone", False)
        super().__init__(*args, **kwargs)

    def process_bind_param(
        self,
        value: Optional[datetime],
        dialect,
    ) -> Optional[datetime]:
        """Convert Python -> DB."""
        if value is None:
            return None
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(
        self,
        value: Optional[datetime],
        dialect,
    ) -> Optional[datetime]:
        """Convert DB -> Python."""
        if value is None:
            return None
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
