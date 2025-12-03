from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .permission import Permission


class Role(Base):
    __tablename__: str = "role"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)

    permissions: Mapped[List[Permission]] = relationship(secondary="role_x_permission")
