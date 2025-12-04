from .contract import Contract
from .course import CourseDB
from .lesson import Lesson
from .odoo import CourseOdoo, LessonOdoo, TeacherOdoo
from .student import Student
from .token import Token
from .user import User, UserContract, UserCreate, UserDB

__all__: list[str] = [
    "Contract",
    "CourseDB",
    "CourseOdoo",
    "Lesson",
    "LessonOdoo",
    "Student",
    "TeacherOdoo",
    "Token",
    "User",
    "UserDB",
    "UserCreate",
    "UserContract",
]
