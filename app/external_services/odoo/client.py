from typing import Any, Dict, List, Optional, Set, cast
from xmlrpc.client import ServerProxy

from bs4 import BeautifulSoup

from app.configuration import configuration
from app.schemas import CourseOdoo, LessonOdoo, TeacherOdoo


class OdooClient:
    def __init__(self) -> None:
        self.url: str = configuration.ODOO_URL.encoded_string()
        self.db: str = configuration.ODOO_DB
        self.user: str = configuration.ODOO_USER
        self.api_key: str = configuration.ODOO_API_KEY.get_secret_value()
        self.common = ServerProxy(uri=f"{self.url}/xmlrpc/2/common", allow_none=True)
        self.models = ServerProxy(uri=f"{self.url}/xmlrpc/2/object", allow_none=True)
        self.uid: str = cast(
            str, self.common.authenticate(self.db, self.user, self.api_key, {})
        )

    def execute_kw(
        self,
        model: str,
        method: str,
        args: list[Any] = [],
        kwargs: Optional[dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        response: List[Dict[str, Any]] = cast(
            List[Dict[str, Any]],
            self.models.execute_kw(
                self.db, self.uid, self.api_key, model, method, args, kwargs
            ),
        )

        return response

    def get_teachers_ids(self) -> Set[int]:
        courses: List[Dict[str, Any]] = self.execute_kw(
            model="slide.channel", method="search_read", kwargs={"fields": ["user_id"]}
        )

        teachers_id: Set[int] = {course["user_id"][0] for course in courses}

        return teachers_id

    def get_teachers(self) -> List[TeacherOdoo]:
        teachers_ids: Set[int] = self.get_teachers_ids()

        teacher_fields: List[str] = ["id", "name", "email", "active"]

        teachers: List[Dict[str, Any]] = self.execute_kw(
            model="res.users",
            method="read",
            args=[list(teachers_ids)],
            kwargs={"fields": teacher_fields},
        )

        return [
            TeacherOdoo(external_reference=teacher["id"], **teacher)
            for teacher in teachers
        ]

    def get_courses(self, teacher_id: int) -> List[CourseOdoo]:
        course_fields: List[str] = [
            "id",
            "name",
            "description",
            "product_id",
        ]
        courses: List[Dict[str, Any]] = self.execute_kw(
            model="slide.channel",
            method="search_read",
            args=[[("user_id", "=", teacher_id)]],
            kwargs={"fields": course_fields, "order": "id asc"},
        )

        return [
            CourseOdoo(
                external_reference=course["id"],
                description=BeautifulSoup(
                    course["description"], "html.parser"
                ).get_text()
                if course["description"]
                else "",
                name=course["name"],
                product_id=course["product_id"][0] if course["product_id"] else None,
            )
            for course in courses
        ]

    def get_course_lessons(self, course_id: int) -> List[LessonOdoo]:
        lesson_fields: List[str] = ["id", "name"]

        lessons: List[Dict[str, Any]] = self.execute_kw(
            model="slide.slide",
            method="search_read",
            args=[[("channel_id", "=", course_id)]],
            kwargs={"fields": lesson_fields},
        )

        return [
            LessonOdoo(external_reference=lesson["id"], **lesson) for lesson in lessons
        ]

    def get_course_sales(self, product_id: int):
        sale_fields: List[str] = ["order_id", "price_total", "product_uom_qty"]

        sales = self.execute_kw(
            model="sale.order.line",
            method="search_read",
            args=[
                [
                    ("product_id", "=", product_id),
                    ("order_id.state", "in", ["sale", "done"]),
                ]
            ],
            kwargs={
                "fields": sale_fields,
            },
        )

        return sales

    def get_students_ids(self, course_id: int):
        student_fields: List[str] = ["partner_ids"]

        students_ids: List[Dict[str, Any]] = self.execute_kw(
            model="slide.channel.partner",
            method="search_read",
            args=[[("channel_id", "=", course_id)]],
            kwargs={
                "fields": student_fields,
                "order": "id desc",
            },
        )

        return students_ids


odoo: OdooClient = OdooClient()
