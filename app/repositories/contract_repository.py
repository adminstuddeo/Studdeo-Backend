from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Contract
from app.schemas import ContractCreate


class InterfaceContractRepository(ABC):
    @abstractmethod
    async def create_contract(self, contract_create: ContractCreate) -> None: ...


@dataclass
class ContractRepository(InterfaceContractRepository):
    async_session: AsyncSession

    async def create_contract(self, contract_create: ContractCreate) -> None:
        contract: Contract = Contract(**contract_create.model_dump())

        self.async_session.add(contract)

        try:
            await self.async_session.commit()

            await self.async_session.refresh(contract)

        except Exception as database_error:
            raise database_error
