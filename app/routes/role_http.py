from typing import List

from fastapi import APIRouter, Depends, Security

from app.database.models import User
from app.enums import Permission
from app.schemas import RoleDB
from app.services import RoleService

from .dependencies import get_current_user, get_role_service

role_router = APIRouter(tags=["Role"], prefix="/role")


@role_router.get("/", response_model=List[RoleDB])
async def route_get_roles(
    role_service: RoleService = Depends(dependency=get_role_service),
    _: User = Security(dependency=get_current_user, scopes=[Permission.CREATE_USER]),
) -> List[RoleDB]:
    return await role_service.get_roles()
