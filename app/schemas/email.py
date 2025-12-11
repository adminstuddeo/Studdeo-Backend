from pydantic import BaseModel, HttpUrl


class UserBaseEmail(BaseModel):
    name: str
    lastname: str
    frontend_url: HttpUrl
    year: int
