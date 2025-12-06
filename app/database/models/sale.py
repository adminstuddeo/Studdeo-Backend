from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .detail_sale import DetailSale


class Sale(Base):
    __tablename__: str = "sale"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    details_sale: Mapped[List[DetailSale]] = relationship()

    external_reference: Mapped[int] = mapped_column(nullable=False)
    buyer_external_reference: Mapped[int] = mapped_column(nullable=False)
