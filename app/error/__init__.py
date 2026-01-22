from .auth_error import BadPassword, BadToken, InsufficientPermissions, InvalidToken
from .course_error import CourseNotFound
from .teacher_error import TeacherNotFound
from .user_error import UserAlreadyExist, UserNotFound

__all__: list[str] = [
    "BadPassword",
    "BadToken",
    "CourseNotFound",
    "InsufficientPermissions",
    "UserAlreadyExist",
    "UserNotFound",
    "TeacherNotFound",
    "InvalidToken",
]
