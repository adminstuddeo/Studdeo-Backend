from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm

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
) -> Response:
    try:
        token: Token = await auth_service.auth_user(
            email=user_login.username, password=user_login.password
        )

        response: Response = Response(
            status_code=status.HTTP_200_OK, content=token.model_dump_json()
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

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Oops... Something went wrong.",
        )
