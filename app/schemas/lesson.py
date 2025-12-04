from pydantic import BaseModel


class Lesson(BaseModel):
    name: str
