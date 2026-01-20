from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Contract(BaseModel):
    percentaje: float
    valid_from: datetime
    valid_to: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Reference(Contract):
    referred_id_user: UUID


class ContractCreate(Reference):
    referer_id_user: UUID
