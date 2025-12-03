from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Contract, UserContract


class InterfaceContractRepository(ABC):
    @abstractmethod
    async def create_contract(
        self,
        referer_id_user: UUID,
        referred_id_user: UUID,
        percentaje: float,
        valid_from: datetime,
        valid_to: Optional[datetime] = None,
    ) -> None: ...


class ContractRepository(InterfaceContractRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self.async_session: AsyncSession = db_session

    async def create_contract(
        self,
        referer_id_user: UUID,
        referred_id_user: UUID,
        percentaje: float,
        valid_from: datetime,
        valid_to: Optional[datetime] = None,
    ) -> None:
        contract: Contract = Contract(
            percentaje=percentaje, valid_from=valid_from, valid_to=valid_to
        )

        contract_x_user: UserContract = UserContract(
            referer_id_user=referer_id_user,
            referred_id_user=referred_id_user,
            contract_id=contract.id,
        )

        self.async_session.add_all([contract, contract_x_user])

        try:
            await self.async_session.commit()

            await self.async_session.refresh(contract)

        except Exception:
            raise
