from .auth_error import BadPassword, BadToken
from .course_error import CourseNotFound
from .user_error import UserAlreadyExist, UserNotFound

__all__: list[str] = [
    "BadPassword",
    "BadToken",
    "CourseNotFound",
    "UserAlreadyExist",
    "UserNotFound",
]
