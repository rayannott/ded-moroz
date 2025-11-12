class TestStartGameInRoom:
    """Start the game.

    Given:
    - a number of registered users
    - a room created by one of the users (the manager)
    When:
    - the manager starts the game in that room
    Then:
    - messages are sent to all room members with their targets
    - the room's state is updated to reflect that the game has started
    """

    # TODO(test): possibly also test when RoomTooSmall
    pass
