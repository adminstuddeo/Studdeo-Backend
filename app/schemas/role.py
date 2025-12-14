from pydantic import BaseModel


class RoleDB(BaseModel):
    id: int
    name: str
