from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Student(Base):
    __tablename__: str = "student"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    external_reference: Mapped[int] = mapped_column()
