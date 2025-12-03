from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Lesson(Base):
    __tablename__: str = "lesson"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    id_course: Mapped[UUID] = mapped_column(ForeignKey("course.id"))
    name: Mapped[str] = mapped_column()

    external_reference: Mapped[int] = mapped_column()
