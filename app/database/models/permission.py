from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Permission(Base):
    __tablename__: str = "permission"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
