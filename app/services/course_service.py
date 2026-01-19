from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Set

from app.repositories import OdooRepository
from app.schemas import CourseOdoo, LessonOdoo, SaleOdoo, StudentOdoo


@dataclass
class CourseService:
    repository: OdooRepository

    def get_all_courses(self, date_from: Optional[datetime] = None) -> List[CourseOdoo]:
        return self.repository.get_all_courses(date_from=date_from)

    def get_courses(self, teacher_id: int) -> List[CourseOdoo]:
        return self.repository.get_courses(teacher_id=teacher_id)

    def get_lessons(self, course_id: int) -> List[LessonOdoo]:
        return self.repository.get_course_lessons(course_id=course_id)

    def get_students(self, course_id: int) -> List[StudentOdoo]:
        students_ids: Set[int] = self.repository.get_students_ids(course_id=course_id)

        return self.repository.get_students(students_ids=students_ids)

    def get_course_sales(self, course_id: int) -> List[SaleOdoo]:
        return self.repository.get_course_sales(course_id)
