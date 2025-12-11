from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Contract, Role, User
from app.enums import Role as RoleEnum
from app.schemas import UserCreate


class InterfaceUserRepository(ABC):
    @abstractmethod
    async def create_user(self, user_create: UserCreate) -> None: ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    async def get_user(self, id_user: UUID) -> Optional[User]: ...

    @abstractmethod
    async def get_users(self, is_active: bool) -> Sequence[User]: ...

    @abstractmethod
    async def update_user(self, user: User) -> None: ...


@dataclass
class UserRepository(InterfaceUserRepository):
    async_session: AsyncSession

    async def create_user(self, user_create: UserCreate) -> None:
        statement: Select[Tuple[Role]] = select(Role).where(
            Role.name == RoleEnum.TEACHER
        )

        result: Result[Tuple[Role]] = await self.async_session.execute(
            statement=statement
        )

        role: Role = result.scalar_one()

        user: User = User(**user_create.model_dump(), id_role=role.id)

        try:
            self.async_session.add(user)
            await self.async_session.commit()

        except Exception as database_error:
            await self.async_session.rollback()
            raise database_error

    async def get_user(self, id_user: UUID) -> Optional[User]:
        try:
            return await self.async_session.get(User, id_user)

        except Exception as database_error:
            raise database_error

    async def get_user_by_email(self, email: str) -> Optional[User]:
        statement: Select[Tuple[User]] = (
            select(User)
            .options(
                selectinload(User.role).selectinload(Role.permissions),
                selectinload(User.contracts).selectinload(Contract.refererred_user),
            )
            .where(User.email == email)
        )

        result: Result[Tuple[User]] = await self.async_session.execute(
            statement=statement
        )

        return result.scalar_one_or_none()

    async def get_users(self, is_active: bool) -> Sequence[User]:
        statement: Select[Tuple[User]] = select(User).where(User.is_active == is_active)

        result: Result[Tuple[User]] = await self.async_session.execute(
            statement=statement
        )

        return result.scalars().fetchall()

    async def update_user(self, user: User) -> None:
        try:
            await self.async_session.commit()

        except Exception as database_error:
            await self.async_session.rollback()
            raise database_error
