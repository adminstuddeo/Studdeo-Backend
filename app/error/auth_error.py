class BadPassword(Exception):
    def __init__(self, message: str = "Wrong password.") -> None:
        super().__init__(message)


class BadToken(Exception):
    def __init__(self, message: str = "Could not validate credentials."):
        super().__init__(message)


class InsufficientPermissions(Exception):
    def __init__(self, message: str = "You don't have sufficients permissions") -> None:
        super().__init__(message)


class InvalidToken(Exception):
    def __init__(self, message: str = "This token is invalid.") -> None:
        super().__init__(message)
