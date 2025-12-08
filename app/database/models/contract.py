from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


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
    valid_to: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    refererred_user: Mapped["User"] = relationship(
        "User", foreign_keys=[referred_id_user]
    )
