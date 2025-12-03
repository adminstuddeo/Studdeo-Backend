from datetime import datetime

from pydantic import BaseModel, EmailStr


class Buyer(BaseModel):
    order_id: int
    order_name: str
    state: str
    date_order: datetime
    partner_id: int
    partner_name: str
    email: EmailStr
