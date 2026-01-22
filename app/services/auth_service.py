from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode  # type: ignore
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, HttpUrl

from app.configuration import configuration
from app.database.models import PasswordResetToken, User
from app.email import EmailClient
from app.enums import TemplateHTML
from app.error import BadPassword, BadToken, InvalidToken, UserNotFound
from app.repositories import (
    InterfacePasswordResetTokenRepository,
    InterfaceUserRepository,
)
from app.schemas import Token, UserBaseEmail
from app.schemas import User as UserDTO

from .security_service import SecurityService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@dataclass
class AuthService:
    repository: InterfaceUserRepository
    password_reset_token_repository: InterfacePasswordResetTokenRepository
    security_service: SecurityService = field(default_factory=SecurityService)

    async def auth_user(self, email: str, password: str) -> Token:
        user: Optional[User] = await self.repository.get_user_by_email(email=email)

        if not user or not user.is_active:
            raise UserNotFound()

        if not self.security_service.verify_password(
            plain_password=password, hashed_password=user.password
        ):
            raise BadPassword()

        user_information: UserDTO = UserDTO(
            name=user.name,
            email=user.email,
            lastname=user.lastname,
            role=user.role.name,
        )

        return self.create_access_token(user_data=user_information)

    async def get_current_user(self, access_token: str) -> User:
        try:
            decoded_jwt: Dict[str, Any] = decode(
                jwt=access_token,
                key=configuration.ENCRYPTION_SECRET_KEY,
                algorithms=[configuration.ENCRYPTION_ALGORITHM],
            )

            email: Optional[str] = decoded_jwt.get("email")

            if not email:
                raise InvalidTokenError()

        except InvalidTokenError:
            raise BadToken()

        user: Optional[User] = await self.repository.get_user_by_email(email=email)

        if not user or not user.is_active:
            raise UserNotFound()

        return user

    def create_access_token(
        self,
        user_data: BaseModel,
        expires_delta: Optional[timedelta] = None,
    ) -> Token:
        if not expires_delta:
            expires_delta = timedelta(minutes=30)

        payload: Dict[str, Any] = {
            "expire": (datetime.now(timezone.utc) + expires_delta).isoformat()
        }

        payload.update(user_data.model_dump())

        encoded_jwt: str = encode(
            payload=payload,
            key=configuration.ENCRYPTION_SECRET_KEY,
            algorithm=configuration.ENCRYPTION_ALGORITHM,
        )

        return Token(access_token=encoded_jwt)

    async def create_email_restore_password(self, email: str) -> None:
        user: Optional[User] = await self.repository.get_user_by_email(email=email)

        if not user or not user.is_active:
            return None

        user_information: UserDTO = UserDTO(
            name=user.name,
            email=user.email,
            lastname=user.lastname,
            role=user.role.name,
        )

        token: Token = self.create_access_token(user_data=user_information)

        await self.password_reset_token_repository.create_password_reset_token(
            token=token.access_token, id_user=user.id
        )

        url: HttpUrl = HttpUrl(
            url=configuration.FRONTEND_URL.encoded_string()
            + f"/token={token.access_token}"
        )

        year: int = datetime.now().year

        email_information = UserBaseEmail(
            name=user.name, lastname=user.lastname, frontend_url=url, year=year
        )

        client: EmailClient = EmailClient()

        await client.send_email(
            subject="Restore passsword",
            email=user.email,
            email_information=email_information,
            template_name=TemplateHTML.RESTORE_PASSWORD,
        )

    async def restore_password(self, hashed_token: str, new_password: str):
        token_db: Optional[
            PasswordResetToken
        ] = await self.password_reset_token_repository.get_password_reset_token(
            token=hashed_token
        )

        if not token_db or token_db.expired_at < datetime.now(timezone.utc):
            raise InvalidToken()

        hashed_password: str = self.security_service.hash_password(new_password)

        token_db.user.password = hashed_password

        await self.repository.update_user(user=token_db.user)

        token_db.is_active = False
