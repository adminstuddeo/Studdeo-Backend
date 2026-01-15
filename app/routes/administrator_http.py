from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.database.models import User
from app.enums import Permission
from app.error import UserNotFound
from app.schemas import CourseOdoo, LessonOdoo
from app.services import CourseService

from .dependencies import get_course_service, get_current_user

administrator_router: APIRouter = APIRouter(
    prefix="/administrator", tags=["Administrator"]
)


@administrator_router.get("/courses", response_model=List[CourseOdoo])
async def router_get_courses(
    comision: Optional[float] = None,
    date_from: Optional[datetime] = None,
    teacher_id: Optional[int] = None,
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_ALL_COURSES]
    ),
    course_service: CourseService = Depends(get_course_service),
) -> List[CourseOdoo]:
    if teacher_id:
        return course_service.get_courses(teacher_id=teacher_id)

    return course_service.get_all_courses(date_from=date_from)


@administrator_router.get(path="/{course_id}/lessons", response_model=List[LessonOdoo])
async def route_get_lessons(
    course_id: int,
    course_service: CourseService = Depends(dependency=get_course_service),
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_LESSONS]
    ),
) -> List[LessonOdoo]:
    if not current_user.external_reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(UserNotFound())
        )

    return course_service.get_lessons(course_id=course_id)
