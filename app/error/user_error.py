class UserNotFound(Exception):
    def __init__(self, message: str = "User not found.") -> None:
        super().__init__(message)


class UserAlreadyExist(Exception):
    def __init__(self, message: str = "The email already exists") -> None:
        super().__init__(message)
