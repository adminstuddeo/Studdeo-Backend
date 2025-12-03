from typing import List

from pydantic import BaseModel, Field

from .buyer import Buyer


class Sale(BaseModel):
    has_product: bool
    product_id: int
    orders: int
    units: int
    revenue: int
    buyers: List[Buyer] = Field(default_factory=list[Buyer])
