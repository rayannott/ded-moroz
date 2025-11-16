class TestKickPlayer:
    """Manager kicks player from the room.

    Given:
        - registered users: u0 (manager), u1 (member)
        - a room created by u0, with u1 as a member
    When:
        - the manager u0 kicks u1 from the room
    Then:
        - u1 should receive a notification about being kicked
        - u1 should no longer be a member of the room

    When:
        - the player is already not in the room (e.g., left by themselves) when the manager tries to kick them
    Then:
        - the manager should be informed that the player is already not in the room
        - a warning should be logged
    """

    # TODO(test)
    pass
