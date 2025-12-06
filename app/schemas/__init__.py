from .contract import Contract
from .course import CourseDB
from .lesson import Lesson
from .odoo import (
    CourseOdoo,
    DetailSaleOdoo,
    LessonOdoo,
    SaleOdoo,
    StudentOdoo,
    TeacherOdoo,
)
from .student import Student
from .token import Token
from .user import User, UserContract, UserCreate, UserDB

__all__: list[str] = [
    "Contract",
    "CourseDB",
    "CourseOdoo",
    "DetailSaleOdoo",
    "Lesson",
    "LessonOdoo",
    "SaleOdoo",
    "Student",
    "StudentOdoo",
    "TeacherOdoo",
    "Token",
    "User",
    "UserDB",
    "UserCreate",
    "UserContract",
]
