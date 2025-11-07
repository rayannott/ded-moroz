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


class RoomNotFound(AppError):
    """Raised when a room is not found."""

    pass


class UserAlreadyExists(AppError):
    """Raised when trying to create a user that already exists."""

    pass
