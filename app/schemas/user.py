from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .contract import Contract, Reference


class User(BaseModel):
    name: str
    lastname: str
    email: EmailStr

    role: Optional[str] = None


class UserCreate(User):
    password: str = Field(min_length=8, pattern=r".*[A-Z].*")
    id_role: int

    model_config = ConfigDict(frozen=True)


class UserDB(User):
    id: UUID
    external_reference: Optional[int] = None


class UserContract(BaseModel):
    external_reference: int
    contract: Contract
    referencies: Optional[List[Reference]] = None

    model_config = ConfigDict(frozen=True)
