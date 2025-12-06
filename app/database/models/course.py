from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .lesson import Lesson
from .student import Student


class Course(Base):
    __tablename__: str = "course"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    registered: Mapped[int] = mapped_column()
    external_reference: Mapped[int] = mapped_column()
    id_user: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    price: Mapped[float] = mapped_column(nullable=True)

    lessons: Mapped[List[Lesson]] = relationship()
    students: Mapped[List[Student]] = relationship(secondary="student_x_course")
