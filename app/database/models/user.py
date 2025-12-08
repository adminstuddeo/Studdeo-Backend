from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import UUID as SQLUUID
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .role import Role

if TYPE_CHECKING:
    from .contract import Contract


class User(Base):
    __tablename__: str = "user"

    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column()
    lastname: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(index=True, unique=True)
    password: Mapped[str] = mapped_column()
    id_role: Mapped[int] = mapped_column(ForeignKey("role.id"))
    external_reference: Mapped[Optional[int]] = mapped_column(
        unique=True, nullable=True
    )

    role: Mapped[Role] = relationship()
    contracts: Mapped[List["Contract"]] = relationship(
        "Contract",
        primaryjoin="User.id == Contract.referer_id_user",
    )

    def activate(self) -> None:
        self.is_active = True

    def set_external_refence(self, external_reference: int) -> None:
        self.external_reference = external_reference
