from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Contract(Base):
    __tablename__: str = "contract"

    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    percentaje: Mapped[float] = mapped_column(nullable=False)
    referer_id_user: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    referred_id_user: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    valid_from: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    )
    valid_to: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
