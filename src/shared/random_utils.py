import random


def random_code() -> str:
    """Generate a random room id."""
    return random.randbytes(4).hex()
