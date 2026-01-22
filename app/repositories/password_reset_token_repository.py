from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import PasswordResetToken


class InterfacePasswordResetTokenRepository(ABC):
    @abstractmethod
    async def create_password_reset_token(self, token: str, id_user: UUID) -> None: ...

    @abstractmethod
    async def get_password_reset_token(
        self, token: str
    ) -> Optional[PasswordResetToken]: ...

    @abstractmethod
    async def update_password_reset_token(
        self, password_reset_token: PasswordResetToken
    ) -> None: ...


@dataclass
class PasswordResetTokenRepository(InterfacePasswordResetTokenRepository):
    async_session: AsyncSession

    async def create_password_reset_token(self, token: str, id_user: UUID) -> None:
        expired_at: datetime = datetime.now(timezone.utc) + timedelta(days=1)

        new_password_reset_token = PasswordResetToken(
            token=token, id_user=id_user, expired_at=expired_at, is_active=True
        )

        self.async_session.add(new_password_reset_token)

        try:
            await self.async_session.commit()

        except Exception as database_error:
            await self.async_session.rollback()
            raise database_error

    async def get_password_reset_token(
        self, token: str
    ) -> Optional[PasswordResetToken]:
        return await self.async_session.get(
            entity=PasswordResetToken,
            ident=token,
            options=[selectinload(PasswordResetToken.user)],
        )

    async def update_password_reset_token(
        self, password_reset_token: PasswordResetToken
    ) -> None:
        try:
            await self.async_session.commit()

        except Exception as database_error:
            await self.async_session.rollback()
            raise database_error
