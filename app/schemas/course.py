from uuid import UUID

from pydantic import BaseModel


class CourseDB(BaseModel):
    id: UUID
    name: str
    description: str
