from typing import Set

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import database
from app.database.models import User
from app.error import BadToken, InsufficientPermissions, UserNotFound
from app.repositories import (
    ContractRepository,
    OdooRepository,
    PasswordResetTokenRepository,
    RoleRepository,
    UserRepository,
)
from app.services import AuthService, CourseService, RoleService, UserService

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_auth_service(
    db_session: AsyncSession = Depends(dependency=database.get_async_session),
) -> AuthService:
    return AuthService(
        repository=UserRepository(async_session=db_session),
        password_reset_token_repository=PasswordResetTokenRepository(
            async_session=db_session
        ),
    )


def get_user_service(
    db_session: AsyncSession = Depends(dependency=database.get_async_session),
) -> UserService:
    return UserService(
        repository=UserRepository(async_session=db_session),
        contract_repository=ContractRepository(async_session=db_session),
    )


def get_course_service() -> CourseService:
    return CourseService(repository=OdooRepository())


async def get_current_user(
    security_scopes: SecurityScopes,
    access_token: str = Depends(dependency=oauth_scheme),
    auth_service: AuthService = Depends(dependency=get_auth_service),
) -> User:
    try:
        user: User = await auth_service.get_current_user(access_token=access_token)

        user_permissions: Set[str] = {
            permission.name for permission in user.role.permissions
        }

        if not set(security_scopes.scopes).issubset(user_permissions):
            raise InsufficientPermissions

        return user

    except (
        UserNotFound,
        InvalidTokenError,
        BadToken,
        InsufficientPermissions,
    ) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))


async def get_role_service(
    db_session: AsyncSession = Depends(dependency=database.get_async_session),
) -> RoleService:
    return RoleService(repository=RoleRepository(async_session=db_session))
