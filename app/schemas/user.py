from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from .contract import Contract, Reference


class User(BaseModel):
    name: str
    lastname: str
    email: EmailStr

    role: str


class UserCreate(User):
    password: str

    model_config = ConfigDict(frozen=True)


class UserDB(User):
    id: UUID
    external_reference: Optional[int] = None


class UserContract(BaseModel):
    external_reference: int
    contract: Contract
    referencies: Optional[List[Reference]] = None

    model_config = ConfigDict(frozen=True)
