from typing import List, Optional, Sequence
from uuid import UUID

from app.database.models import Course
from app.repositories import InterfaceCourseRepository
from app.schemas import CourseDB, Lesson


class CourseService:
    def __init__(self, repository: InterfaceCourseRepository) -> None:
        self.repository: InterfaceCourseRepository = repository

    async def get_lessons(self, id_course: UUID) -> List[Lesson]:
        course: Optional[Course] = await self.repository.get_course(id_course=id_course)

        if not course:
            raise

        return [Lesson.model_validate(lesson) for lesson in course.lessons]

    async def get_courses(self, id_user: UUID) -> List[CourseDB]:
        courses: Sequence[Course] = await self.repository.get_courses(id_user=id_user)

        return [CourseDB.model_validate(course) for course in courses]
