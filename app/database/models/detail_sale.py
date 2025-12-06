from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class DetailSale(Base):
    __tablename__: str = "detail_sale"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    external_reference: Mapped[int] = mapped_column()
    sale_id: Mapped[UUID] = mapped_column(ForeignKey("sale.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    quantity: Mapped[float] = mapped_column()
    price_unit: Mapped[float] = mapped_column()
