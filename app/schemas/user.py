from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from .contract import Contract, Reference


class User(BaseModel):
    name: str
    lastname: str
    email: EmailStr


class UserCreate(User):
    password: str

    model_config = ConfigDict(frozen=True)


class UserDB(User):
    id: UUID
    external_reference: int


class UserContract(BaseModel):
    external_reference: int
    contract: Contract
    referencies: List[Reference]

    model_config = ConfigDict(frozen=True)
