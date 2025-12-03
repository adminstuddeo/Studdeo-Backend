from typing import Any, List
from uuid import UUID

from pydantic import BaseModel, Field

from .lesson import Lesson


class CourseOdoo(BaseModel):
    id: int
    name: str
    website_published: bool
    description: str
    responsable: str
    inscritos: int
    inscritos_detalle: List[Any] = Field(default_factory=list)
    user_id: int
    product_id: int


class CourseDB(BaseModel):
    id: UUID
    name: str
    description: str


class Course(CourseDB):
    lessons: List[Lesson]
