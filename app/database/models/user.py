from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .contract import Contract
from .role import Role


class User(Base):
    __tablename__: str = "user"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    lastname: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(index=True, unique=True)
    password: Mapped[str] = mapped_column()
    id_role: Mapped[int] = mapped_column(ForeignKey("role.id"))
    external_reference: Mapped[int] = mapped_column(unique=True, nullable=True)
    latest_sync: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    role: Mapped[Role] = relationship()
    contract: Mapped[List[Contract]] = relationship(
        secondary="user_x_contract",
        primaryjoin="User.id == UserContract.referer_id_user",
        secondaryjoin="UserContract.contract_id == Contract.id",
        viewonly=True,
    )

    def activate(self) -> None:
        self.is_active = True

    def set_external_refence(self, external_reference: int) -> None:
        self.external_reference = external_reference
