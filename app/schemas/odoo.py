from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, computed_field


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
    details_sale: List[DetailSaleOdoo]
    buyer: StudentOdoo

    @computed_field
    def calculated_subtotal(self) -> float:
        subtotal: float = 0

        for detail in self.details_sale:
            subtotal += detail.price * detail.quantity

        return subtotal


class CourseOdoo(BaseModel):
    external_reference: int
    name: str
    description: str
    product_id: Optional[int] = None
    user_id: int


class CourseWithSales(CourseOdoo):
    sales: List[SaleOdoo] = Field(default_factory=list[SaleOdoo])

    @computed_field
    def calculated_total(self) -> float:
        total: float = 0

        for subtotal in self.sales:
            total += subtotal.calculated_subtotal()

        return total
