class AppError(Exception):
    """Base class for application-specific exceptions."""

    pass


class MaxNumberOfRoomsReached(AppError):
    """Raised when the maximum number of rooms has been reached."""

    pass


class UserNotFound(AppError):
    """Raised when a user is not found."""

    pass


class AlreadyInRoom(AppError):
    """Raised when a user is already in a room."""

    pass


class NotInRoom(AppError):
    """Raised when a user is not in a room."""

    pass


class GameAlreadyStarted(AppError):
    """Raised when trying to start a game that has already started."""

    pass


class GameAlreadyCompleted(AppError):
    """Raised when trying to complete a game that has already been completed."""

    pass


class RoomNotFound(AppError):
    """Raised when a room is not found."""

    pass


class UserAlreadyExists(AppError):
    """Raised when trying to create a user that already exists."""

    pass


class RoomTooSmall(AppError):
    """Raised when game is attempted to start in a room with too few players."""

    pass


class TargetNotAssigned(AppError):
    """Raised when a target could not be assigned to a player."""

    pass


class InvalidName(AppError):
    """Raised when a provided name is invalid."""

    pass
