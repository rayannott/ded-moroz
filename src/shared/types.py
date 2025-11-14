from dataclasses import dataclass


@dataclass
class Status:
    res: bool
    reason: str | None = None

    def __bool__(self) -> bool:
        return self.res
