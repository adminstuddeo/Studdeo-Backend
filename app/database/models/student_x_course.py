from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class StudentCourse(Base):
    __tablename__: str = "student_x_course"

    id_course: Mapped[UUID] = mapped_column(ForeignKey("course.id"), primary_key=True)
    id_student: Mapped[UUID] = mapped_column(ForeignKey("student.id"), primary_key=True)
