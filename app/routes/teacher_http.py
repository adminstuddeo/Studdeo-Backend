from fastapi import APIRouter, Depends

from app.services import UserService

from .dependencies import get_user_service

teacher_router: APIRouter = APIRouter(prefix="/profesores", tags=["Profesor Odoo"])


@teacher_router.get(path="/")
def route_get_teachers(
    user_service: UserService = Depends(get_user_service),
    # current_user: User = Security(
    #   get_current_user, scopes=[Permission.READ_EXTERNAL_USERS]
    # ),
): ...


# 1 Un endpoint que me traiga los usuarios con nombre, apellido, mail, id (external_reference), filtrando los que ya estan en
# nuestra base de datos
