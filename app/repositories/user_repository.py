from abc import ABC, abstractmethod
from typing import Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
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


class UserRepository(InterfaceUserRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self.async_session: AsyncSession = db_session

    async def create_user(self, user_create: UserCreate) -> None:
        user: User = User(**user_create.model_dump())

        try:
            self.async_session.add(user)
            await self.async_session.commit()

        except Exception:
            await self.async_session.rollback()

    async def get_user(self, id_user: UUID) -> Optional[User]:
        try:
            return await self.async_session.get(User, id_user)

        except Exception as database_error:
            raise database_error

    async def get_user_by_email(self, email: str) -> Optional[User]:
        statement: Select[Tuple[User]] = select(User).where(User.email == email)

        try:
            result: Result[Tuple[User]] = await self.async_session.execute(
                statement=statement
            )

            return result.scalar_one_or_none()

        except Exception as database_error:
            raise database_error

    async def get_users(self, is_active: bool) -> Sequence[User]:
        statement: Select[Tuple[User]] = select(User).where(User.is_active == is_active)

        result: Result[Tuple[User]] = await self.async_session.execute(
            statement=statement
        )

        return result.scalars().fetchall()

    async def update_user(self, user: User) -> None:
        try:
            self.async_session.add(user)

            await self.async_session.commit()

        except Exception:
            await self.async_session.rollback()
