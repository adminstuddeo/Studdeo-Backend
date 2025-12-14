from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence, Tuple

from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Role


class InterfaceRoleRepository(ABC):
    @abstractmethod
    async def get_roles(self) -> Sequence[Role]: ...


@dataclass
class RoleRepository(InterfaceRoleRepository):
    async_session: AsyncSession

    async def get_roles(self) -> Sequence[Role]:
        statement: Select[Tuple[Role]] = select(Role)

        result: Result[Tuple[Role]] = await self.async_session.execute(
            statement=statement
        )

        return result.scalars().fetchall()
