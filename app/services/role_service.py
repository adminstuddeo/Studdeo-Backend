from dataclasses import dataclass
from typing import List

from app.repositories import RoleRepository
from app.schemas import RoleDB


@dataclass
class RoleService:
    repository: RoleRepository

    async def get_roles(self) -> List[RoleDB]:
        return [
            RoleDB.model_validate(role) for role in await self.repository.get_roles()
        ]
