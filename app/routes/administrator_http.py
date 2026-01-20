from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Security

from app.database.models import User
from app.enums import Permission
from app.schemas import CourseOdoo, CourseWithSales, LessonOdoo, SaleOdoo, UserDB
from app.services import CourseService, UserService

from .dependencies import get_course_service, get_current_user, get_user_service

administrator_router: APIRouter = APIRouter(
    prefix="/administrator", tags=["Administrator"]
)


@administrator_router.get("/courses", response_model=List[CourseOdoo])
async def router_get_courses(
    comision: Optional[float] = None,
    date_from: Optional[datetime] = None,
    teacher_id: Optional[int] = None,
    _: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_ALL_COURSES]
    ),
    course_service: CourseService = Depends(get_course_service),
) -> List[CourseOdoo]:
    if teacher_id:
        return course_service.get_courses(teacher_id=teacher_id)

    return course_service.get_all_courses(date_from=date_from)


@administrator_router.get("/sales", response_model=List[CourseWithSales])
async def router_get_sales(
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_ALL_SALES]
    ),
    user_service: UserService = Depends(get_user_service),
    course_service: CourseService = Depends(get_course_service),
) -> List[CourseWithSales]:
    courses_with_sales: List[CourseWithSales] = []

    users: List[UserDB] = await user_service.get_users(is_active=True)

    for user in users:
        if not user.external_reference:
            continue

        courses: List[CourseOdoo] = course_service.get_courses(
            teacher_id=user.external_reference
        )

        for course in courses:
            if course.product_id:
                sales: List[SaleOdoo] = course_service.get_course_sales(
                    course_id=course.product_id, discount=user.contract.percentaje
                )
                courses_with_sales.append(
                    CourseWithSales(**course.model_dump(), sales=sales)
                )

    return courses_with_sales


@administrator_router.get(
    path="/course/{course_id}/lessons", response_model=List[LessonOdoo]
)
async def route_get_lessons(
    course_id: int,
    course_service: CourseService = Depends(dependency=get_course_service),
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_ALL_LESSONS]
    ),
) -> List[LessonOdoo]:
    return course_service.get_lessons(course_id=course_id)
