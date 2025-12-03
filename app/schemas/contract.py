from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Contract(BaseModel):
    percentaje: float
    valid_from: datetime
    valid_to: Optional[datetime] = None


class Reference(Contract):
    referred_id_user: UUID
