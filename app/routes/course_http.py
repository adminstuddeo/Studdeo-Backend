from typing import List, Set

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.database.models import User
from app.enums import Permission
from app.error import CourseNotFound
from app.schemas import CourseOdoo, LessonOdoo, StudentOdoo
from app.services import CourseService

from .dependencies import get_course_service, get_current_user

course_router: APIRouter = APIRouter(prefix="/course", tags=["Course"])


@course_router.get(path="/", response_model=List[CourseOdoo])
async def route_get_courses(
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_COURSES]
    ),
    course_service: CourseService = Depends(dependency=get_course_service),
) -> List[CourseOdoo]:
    return course_service.get_courses(teacher_id=current_user.external_reference)


@course_router.get(path="/{course_id}/lessons", response_model=List[LessonOdoo])
async def route_get_lessons(
    course_id: int,
    course_service: CourseService = Depends(dependency=get_course_service),
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_LESSONS]
    ),
) -> List[LessonOdoo]:
    try:
        user_courses: Set[int] = {
            course.external_reference
            for course in course_service.get_courses(
                teacher_id=current_user.external_reference
            )
        }

        if course_id not in user_courses:
            raise CourseNotFound()

        return course_service.get_lessons(course_id=course_id)

    except CourseNotFound as course_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(course_error)
        )


@course_router.get(path="/{id_course}/students", response_model=List[StudentOdoo])
async def route_get_students(
    course_id: int,
    course_service: CourseService = Depends(dependency=get_course_service),
    current_user: User = Security(
        dependency=get_current_user, scopes=[Permission.READ_STUDENTS]
    ),
) -> List[StudentOdoo]:
    try:
        user_courses: Set[int] = {
            course.external_reference
            for course in course_service.get_courses(
                teacher_id=current_user.external_reference
            )
        }

        if course_id not in user_courses:
            raise CourseNotFound()

        return course_service.get_students(course_id=course_id)

    except CourseNotFound as course_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(course_error)
        )
