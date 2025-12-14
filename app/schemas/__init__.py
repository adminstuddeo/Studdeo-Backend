from .contract import Contract, ContractCreate
from .email import UserBaseEmail
from .odoo import (
    CourseOdoo,
    DetailSaleOdoo,
    LessonOdoo,
    SaleOdoo,
    StudentOdoo,
    TeacherOdoo,
)
from .role import RoleDB
from .token import Token
from .user import User, UserContract, UserCreate, UserDB

__all__: list[str] = [
    "Contract",
    "ContractCreate",
    "CourseOdoo",
    "DetailSaleOdoo",
    "LessonOdoo",
    "RoleDB",
    "SaleOdoo",
    "StudentOdoo",
    "TeacherOdoo",
    "Token",
    "User",
    "UserDB",
    "UserCreate",
    "UserBaseEmail",
    "UserContract",
]
