from typing import List

from fastapi import APIRouter, Depends

from app.schemas import RoleDB
from app.services import RoleService

from .dependencies import get_role_service

role_router = APIRouter(tags=["Role"], prefix="/role")


@role_router.get("/", response_model=List[RoleDB])
async def route_get_roles(
    role_service: RoleService = Depends(dependency=get_role_service),
) -> List[RoleDB]:
    return await role_service.get_roles()
