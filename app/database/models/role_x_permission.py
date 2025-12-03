from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RolePermission(Base):
    __tablename__: str = "role_x_permission"

    id_role: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)
    id_permission: Mapped[int] = mapped_column(
        ForeignKey("permission.id"), primary_key=True
    )
