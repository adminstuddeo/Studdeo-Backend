from typing import List

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import database
from app.database.models.user import User
from app.error import UserNotFound
from app.repositories import ContractRepository, CourseRepository, UserRepository
from app.services import AuthService, CourseService, UserService

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_auth_service(
    db_session: AsyncSession = Depends(dependency=database.get_async_session),
) -> AuthService:
    return AuthService(repository=UserRepository(db_session=db_session))


def get_user_service(
    db_session: AsyncSession = Depends(dependency=database.get_async_session),
) -> UserService:
    return UserService(
        repository=UserRepository(db_session=db_session),
        contract_repository=ContractRepository(db_session=db_session),
    )


def get_course_service(
    db_session: AsyncSession = Depends(dependency=database.get_async_session),
) -> CourseService:
    return CourseService(repository=CourseRepository(db_session=db_session))


async def get_current_user(
    security_scopes: SecurityScopes,
    access_token: str = Depends(dependency=oauth_scheme),
    auth_service: AuthService = Depends(dependency=get_auth_service),
) -> User:
    try:
        user: User = await auth_service.get_current_user(access_token=access_token)

        user_permissions: List[str] = [
            permission.name for permission in user.role.permissions
        ]

        for permission in security_scopes.scopes:
            if permission not in user_permissions:
                raise  # TODO: Crear excepcion

        return user

    except UserNotFound:
        raise
