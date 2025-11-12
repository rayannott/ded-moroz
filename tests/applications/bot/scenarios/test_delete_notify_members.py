class TestRoomDeletedNotifyMembers:
    """Notifying members when a room is deleted.

    Given:
        - registered users: u0 (manager), u1, u2 (members), u3 (neither)
        - a room created by u0, with u1 and u2 as members
    When:
        - the manager u0 deletes the room
    Then:
        - u1 and u2 should receive a notification about the room deletion
        - u3 should not receive any notification
    """

    # TODO(test)
    pass
