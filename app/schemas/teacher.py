from pydantic import BaseModel, EmailStr


class Teacher(BaseModel):
    id: int
    name: str
    login: EmailStr
    email: EmailStr
    active: bool
