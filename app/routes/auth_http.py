import logfire
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.configuration import configuration
from app.enums import Environment
from app.error import BadPassword, UserNotFound
from app.schemas import Token
from app.services import AuthService

from .dependencies import get_auth_service

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Authenticacion"])


@auth_router.post(path="/login", response_model=Token)
async def login_user(
    user_login: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(dependency=get_auth_service),
) -> JSONResponse:
    try:
        token: Token = await auth_service.auth_user(
            email=user_login.username, password=user_login.password
        )

        response: JSONResponse = JSONResponse(
            status_code=status.HTTP_200_OK, content=token.model_dump()
        )

        response.set_cookie(
            key="access_token",
            value=token.access_token,
            samesite="lax",
            secure=configuration.environment == Environment.PRODUCTION,
        )

        return response

    except (UserNotFound, BadPassword) as auth_error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(auth_error)
        )

    except Exception as error:
        logfire.error(f"Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Oops... Something went wrong.",
        )


@auth_router.post(path="/restore_password")
async def route_restore_password(
    email: EmailStr, auth_service: AuthService = Depends(get_auth_service)
) -> JSONResponse:
    try:
        await auth_service.create_email_restore_password(email=email)

        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"message": "Si el mail existe, se enviaran instrucciones."},
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )


@auth_router.get("/restore_password/{token}")
async def route_update_password(
    token: str,
    new_password: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    try:
        await auth_service.restore_password(
            hashed_token=token, new_password=new_password
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Contraseña actualizada con exito."},
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
