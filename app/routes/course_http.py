from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Security

from app.database.models import User
from app.enums import Permission
from app.schemas import CourseDB, Lesson
from app.services import CourseService

from .dependencies import get_course_service, get_current_user

course_router: APIRouter = APIRouter(prefix="/course", tags=["Course"])

# TODO: Implementar seguro de permisos a las rutas


@course_router.get("/", response_model=List[CourseDB])
async def route_get_courses(
    current_user: User = Security(get_current_user, scopes=[Permission.CREATE_USER]),
    course_service: CourseService = Depends(get_course_service),
) -> List[CourseDB]:
    return await course_service.get_courses(id_user=current_user.id)


@course_router.get("/{id_course}/lessons", response_model=List[Lesson])
async def route_get_course(
    id_course: UUID, course_service: CourseService = Depends(get_course_service)
) -> List[Lesson]:
    return await course_service.get_lessons(id_course=id_course)
