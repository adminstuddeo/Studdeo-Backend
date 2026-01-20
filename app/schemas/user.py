from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .contract import Contract, Reference


class User(BaseModel):
    name: str
    lastname: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True, frozen=True)


class UserCreate(User):
    password: str = Field(min_length=8, pattern=r".*[A-Z].*")
    contract: Contract


class UserDB(User):
    id: UUID
    external_reference: Optional[int] = None
    contract: Contract


class UserContract(BaseModel):
    contract: Contract
    referencies: Optional[List[Reference]] = None
