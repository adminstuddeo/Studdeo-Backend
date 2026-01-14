from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Security

from app.database.models import User
from app.enums import Permission
from app.schemas import CourseOdoo
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
