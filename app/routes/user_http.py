from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import JSONResponse

from app.database.models import User
from app.enums import Permission
from app.error import UserAlreadyExist, UserNotFound
from app.schemas import Contract, UserContract, UserCreate, UserDB
from app.services import UserService

from .dependencies import get_current_user, get_user_service

user_router: APIRouter = APIRouter(prefix="/user", tags=["User"])


@user_router.get(path="/", response_model=List[UserDB])
async def route_get_users(
    is_active: bool = True,
    user_service: UserService = Depends(dependency=get_user_service),
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_USERS]
    ),
) -> List[UserDB]:
    return await user_service.get_users(is_active=is_active)


@user_router.post(path="/")
async def route_create_user(
    user_create: UserCreate,
    user_service: UserService = Depends(dependency=get_user_service),
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.CREATE_USER]
    ),
) -> JSONResponse:
    try:
        await user_service.create_user(user_create=user_create)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content="User successfully created"
        )

    except UserAlreadyExist as user_error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(user_error)
        )


@user_router.get(path="/{id_user}/sales")
async def route_get_sales(): ...


@user_router.post(path="/{id_user}")
async def route_update_user(
    id_user: UUID,
    user_information: UserContract,
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.UPDATE_USER]
    ),
    user_service: UserService = Depends(dependency=get_user_service),
) -> JSONResponse:
    try:
        await user_service.activate_user(
            id_user=id_user, external_reference=user_information.external_reference
        )

        await user_service.create_contract(
            referer_id_user=current_user.id,
            referred_id_user=id_user,
            contract=user_information.contract,
        )

        for reference in user_information.referencies:
            await user_service.create_contract(
                referer_id_user=id_user,
                referred_id_user=reference.referred_id_user,
                contract=Contract.model_validate(reference),
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"User updated succesfully"}
        )

    except UserNotFound as user_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(user_error)
        )
