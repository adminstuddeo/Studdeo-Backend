from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class StudentOdoo(BaseModel):
    external_reference: int
    name: str
    email: Optional[EmailStr] = None


class TeacherOdoo(BaseModel):
    external_reference: int
    name: str
    lastname: str
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
    details_sale: List[DetailSaleOdoo]
    buyer: StudentOdoo
    discount: float
    total: float
    contract_discount: float


class CourseOdoo(BaseModel):
    external_reference: int
    name: str
    description: str
    product_id: Optional[int] = None
    user_id: int
    create_date: datetime
    image: HttpUrl


class CourseWithSales(CourseOdoo):
    sales: List[SaleOdoo] = Field(default_factory=list[SaleOdoo])
