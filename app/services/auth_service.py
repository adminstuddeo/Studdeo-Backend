from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode  # type: ignore
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from app.configuration import configuration
from app.database.models import User
from app.error import BadPassword, BadToken, UserNotFound
from app.repositories import InterfaceUserRepository
from app.schemas import Teacher, Token

from .security_service import SecurityService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:
    def __init__(self, repository: InterfaceUserRepository) -> None:
        self.repository: InterfaceUserRepository = repository
        self.security_service: SecurityService = SecurityService()

    async def auth_user(self, email: str, password: str) -> Token:
        user: Optional[User] = await self.repository.get_user_by_email(email=email)

        if not user:
            raise UserNotFound()

        if not self.security_service.verify_password(
            plain_password=password, hashed_password=user.password
        ):
            raise BadPassword()

        user_information: Teacher = Teacher.model_validate(obj=user)

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

        if not user:
            raise UserNotFound()

        return user

    def create_access_token(
        self,
        user_data: BaseModel,
        expires_delta: timedelta = timedelta(minutes=30),
    ) -> Token:
        payload: Dict[str, Any] = {"expire": expires_delta}

        payload.update(**user_data.model_dump())

        encoded_jwt: str = encode(
            payload=payload,
            key=configuration.ENCRYPTION_SECRET_KEY,
            algorithm=configuration.ENCRYPTION_ALGORITHM,
        )

        return Token(access_token=encoded_jwt)
