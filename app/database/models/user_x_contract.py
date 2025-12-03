from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserContract(Base):
    __tablename__: str = "user_x_contract"

    referer_id_user: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"), primary_key=True
    )
    referred_id_user: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"), primary_key=True
    )
    contract_id: Mapped[UUID] = mapped_column(
        ForeignKey("contract.id"), primary_key=True
    )
