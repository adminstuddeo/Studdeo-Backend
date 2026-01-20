from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Role, User
from app.schemas import UserCreate


class InterfaceUserRepository(ABC):
    @abstractmethod
    async def create_user(self, user_create: UserCreate) -> User: ...

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

    async def create_user(self, user_create: UserCreate) -> User:
        statement: Select[Tuple[Role]] = select(Role).where(
            Role.name == user_create.role
        )

        result: Result[Tuple[Role]] = await self.async_session.execute(
            statement=statement
        )

        role: Role = result.scalar_one()

        user: User = User(
            name=user_create.name,
            lastname=user_create.lastname,
            password=user_create.password,
            email=user_create.email,
            id_role=role.id,
            is_active=True,
        )

        try:
            self.async_session.add(user)
            await self.async_session.commit()

            return user

        except Exception as database_error:
            await self.async_session.rollback()
            raise database_error

    async def get_user(self, id_user: UUID) -> Optional[User]:
        return await self.async_session.get(User, id_user)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        statement: Select[Tuple[User]] = (
            select(User)
            .options(
                selectinload(User.role).selectinload(Role.permissions),
                selectinload(User.contract),
            )
            .where(User.email == email)
        )

        result: Result[Tuple[User]] = await self.async_session.execute(
            statement=statement
        )

        return result.scalar_one_or_none()

    async def get_users(self, is_active: bool) -> Sequence[User]:
        statement: Select[Tuple[User]] = (
            select(User)
            .where(User.is_active == is_active)
            .options(selectinload(User.role), selectinload(User.contract))
        )

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
