from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Security

from app.database.models import User
from app.enums import Permission
from app.schemas import CourseDB, Lesson
from app.schemas.student import Student
from app.services import CourseService

from .dependencies import get_course_service, get_current_user

course_router: APIRouter = APIRouter(prefix="/course", tags=["Course"])


@course_router.get(path="/", response_model=List[CourseDB])
async def route_get_courses(
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_COURSES]
    ),
    course_service: CourseService = Depends(dependency=get_course_service),
) -> List[CourseDB]:
    return await course_service.get_courses(id_user=current_user.id)


@course_router.get(path="/{id_course}/lessons", response_model=List[Lesson])
async def route_get_lessons(
    id_course: UUID,
    course_service: CourseService = Depends(dependency=get_course_service),
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_LESSONS]
    ),
) -> List[Lesson]:
    for course in current_user.courses:
        if course.id == id_course:
            return [Lesson.model_validate(lesson) for lesson in course.lessons]

    return await course_service.get_lessons(id_course=id_course)


@course_router.get(path="/{id_course}/students", response_model=List[Student])
async def route_get_students(
    id_course: UUID,
    course_service: CourseService = Depends(dependency=get_course_service),
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_STUDENTS]
    ),
) -> List[Student]:
    if not await course_service.get_courses(id_user=current_user.id):
        raise

    return await course_service.get_students(id_course=id_course)
