from .contract import Contract
from .odoo import (
    CourseOdoo,
    DetailSaleOdoo,
    LessonOdoo,
    SaleOdoo,
    StudentOdoo,
    TeacherOdoo,
)
from .token import Token
from .user import User, UserContract, UserCreate, UserDB

__all__: list[str] = [
    "Contract",
    "CourseOdoo",
    "DetailSaleOdoo",
    "LessonOdoo",
    "SaleOdoo",
    "StudentOdoo",
    "TeacherOdoo",
    "Token",
    "User",
    "UserDB",
    "UserCreate",
    "UserContract",
]
