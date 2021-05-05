
class NoSuchRoomError(Exception):
    pass  # TODO Add logging to all Exceptions
    # TODO Add exceptions to Exceptions file


class NotEnoughPlayersError(Exception):
    pass


class GameAlreadyStartedError(Exception):
    pass


class CanNotEnterRoomError(Exception):
    pass
