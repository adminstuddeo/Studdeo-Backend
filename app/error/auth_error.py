class BadPassword(Exception):
    def __init__(self, message: str = "Wrong password.") -> None:
        super().__init__(message)


class BadToken(Exception):
    def __init__(self, message: str = "Could not validate credentials."):
        super().__init__(message)
