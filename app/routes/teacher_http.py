from typing import List, Set

from fastapi import APIRouter, Depends, Security

from app.database.models import User
from app.enums import Permission
from app.schemas.odoo import TeacherOdoo
from app.services import UserService

from .dependencies import get_current_user, get_user_service

teacher_router: APIRouter = APIRouter(prefix="/profesores", tags=["Odoo Teachers"])


@teacher_router.get(path="/")
async def route_get_teachers(
    already_mapped: bool = False,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_EXTERNAL_USERS]
    ),
) -> List[TeacherOdoo]:
    users_ids: Set[int] = set()
    if already_mapped:
        users_ids = {
            user.external_reference for user in await user_service.get_users(True)
        }

    return user_service.get_external_users(teacher_ids=users_ids)
