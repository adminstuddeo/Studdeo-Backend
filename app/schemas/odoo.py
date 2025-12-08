from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class StudentOdoo(BaseModel):
    external_reference: int
    name: str
    emai: Optional[EmailStr] = None
    phone: Optional[str] = None


class TeacherOdoo(BaseModel):
    external_reference: int
    name: str
    email: EmailStr
    active: bool


class LessonOdoo(BaseModel):
    external_reference: int
    name: str


class DetailSaleOdoo(BaseModel):
    price: float
    quantity: int
    external_reference: int


class SaleOdoo(BaseModel):
    external_reference: int
    date: datetime
    detail_sale: List[DetailSaleOdoo]
    buyer: StudentOdoo


class CourseOdoo(BaseModel):
    external_reference: int
    name: str
    description: str
    product_id: Optional[int] = None
    sales: Optional[List[SaleOdoo]] = None
