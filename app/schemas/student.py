from pydantic import BaseModel, EmailStr


class Student(BaseModel):
    name: str
    lastname: str
    email: EmailStr
