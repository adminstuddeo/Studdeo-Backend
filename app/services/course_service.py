from typing import List, Set

from app.repositories import OdooRepository
from app.schemas import CourseOdoo, LessonOdoo, StudentOdoo


class CourseService:
    def __init__(self, repository: OdooRepository) -> None:
        self.repository: OdooRepository = repository

    def get_courses(self, teacher_id: int) -> List[CourseOdoo]:
        return self.repository.get_courses(teacher_id=teacher_id)

    def get_lessons(self, course_id: int) -> List[LessonOdoo]:
        return self.repository.get_course_lessons(course_id=course_id)

    def get_students(self, course_id: int) -> List[StudentOdoo]:
        students_ids: Set[int] = self.repository.get_students_ids(course_id=course_id)

        return self.repository.get_students(students_ids=students_ids)
