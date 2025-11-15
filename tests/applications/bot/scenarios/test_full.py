class TestFull:
    """Full scenario test.

    When:
    - u1 starts bot, creates a room, joins it
    - u2 starts bot, joins the room created by u1
    - u1 attempts to start the game
    Then:
    - the game is not started due to insufficient players
    When:
    - u3 starts bot, joins the room created by u1, sets their custom name
    - u4 starts bot, joins the room created by u1
    - u5 starts bot, joins the room created by u1
    - u1 views info about the room (=>the info is correct)
    - u1 kicks u4 from the room
    - u5 leaves the room
    - u1 starts the game
    Then:
    - the game is started successfully
    - the correct notifications are sent to u1, u2, u3
    - the room's state is updated to reflect that the game has started
    When:
    - u1 completes the game
    Then:
    - the game is marked as completed
    - the correct notifications are sent to u1, u2, u3
    - the room's state is updated to reflect that the game has completed
    """

    # TODO(test): full scenario test covering multiple interactions
    pass
