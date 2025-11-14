from src.shared.types import Status


def is_name_valid(name: str) -> Status:
    """Check if the provided name is valid."""
    if not name:
        return Status(False, "cannot be empty")
    if len(name) > 50:
        return Status(False, "cannot be longer than 50 characters")
    if not all(c.isalpha() or c.isspace() for c in name):
        return Status(False, "can only contain letters and spaces")
    return Status(True)
