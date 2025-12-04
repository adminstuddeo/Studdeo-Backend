from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class TeacherOdoo(BaseModel):
    external_reference: int
    name: str
    email: EmailStr
    active: bool


class CourseOdoo(BaseModel):
    external_reference: int
    name: str
    description: str
    product_id: Optional[int] = None


class LessonOdoo(BaseModel):
    external_reference: int
    name: str


class Buyer(BaseModel):
    order_id: int
    order_name: str
    state: str
    date_order: datetime
    partner_id: int
    partner_name: str
    email: EmailStr


class Sale(BaseModel):
    has_product: bool
    product_id: int
    orders: int
    units: int
    revenue: int
    buyers: List[Buyer] = Field(default_factory=list[Buyer])
