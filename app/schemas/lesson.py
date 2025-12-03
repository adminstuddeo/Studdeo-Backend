from typing import Tuple, Union

from pydantic import BaseModel


class LessonOdoo(BaseModel):
    id: int
    name: str
    slide_type: Union[bool, str]
    category_id: Union[bool, Tuple[int, str]]


class Lesson(BaseModel):
    name: str
