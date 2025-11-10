from datetime import datetime
from zoneinfo import ZoneInfo


def utcnow() -> datetime:
    return datetime.now(tz=ZoneInfo("UTC"))
