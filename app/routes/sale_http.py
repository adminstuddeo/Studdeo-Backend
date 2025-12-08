from typing import List

from fastapi import APIRouter, Depends, Security

from app.database.models import User
from app.enums import Permission
from app.schemas import CourseOdoo
from app.services import CourseService

from .dependencies import get_course_service, get_current_user

sale_router: APIRouter = APIRouter(prefix="/sales", tags=["Sales"])


@sale_router.get(path="/", response_model=List[CourseOdoo])
def route_get_sales_user(
    current_user: User = Security(get_current_user, scopes=[Permission.READ_SALES]),
    course_service: CourseService = Depends(get_course_service),
) -> List[CourseOdoo]:
    courses: List[CourseOdoo] = course_service.get_courses(
        teacher_id=current_user.external_reference
    )

    for course in courses:
        if course.product_id:
            course.sales = course_service.get_course_sales(course_id=course.product_id)

    return courses
