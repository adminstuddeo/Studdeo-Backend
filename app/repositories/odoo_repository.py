from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast
from xmlrpc.client import ServerProxy

from bs4 import BeautifulSoup

from app.configuration import configuration
from app.schemas import (
    CourseOdoo,
    DetailSaleOdoo,
    LessonOdoo,
    SaleOdoo,
    StudentOdoo,
    TeacherOdoo,
)


@dataclass
class OdooRepository:
    url: str = configuration.ODOO_URL.encoded_string()
    db: str = configuration.ODOO_DB
    user: str = configuration.ODOO_USER
    api_key: str = configuration.ODOO_API_KEY.get_secret_value()
    common = ServerProxy(uri=f"{url}/xmlrpc/2/common", allow_none=True)
    models = ServerProxy(uri=f"{url}/xmlrpc/2/object", allow_none=True)
    uid: str = cast(str, common.authenticate(db, user, api_key, {}))

    def execute_kw(
        self,
        model: str,
        method: str,
        args: List[List[Union[str, int, Tuple[str, str, Any]]]] = [],
        kwargs: Optional[dict[str, Union[List[str], str]]] = None,
    ) -> List[Dict[str, Any]]:
        response: List[Dict[str, Any]] = cast(
            List[Dict[str, Any]],
            self.models.execute_kw(
                self.db, self.uid, self.api_key, model, method, args, kwargs
            ),
        )

        return response

    def get_database_information(self) -> List[Dict[str, Any]]:
        database_fields: List[str] = ["model", "name", "relation", "help"]

        result: List[Dict[str, Any]] = self.execute_kw(
            model="ir.model", method="search_read", kwargs={"fields": database_fields}
        )

        return result

    def get_table_information(self, table_name: str) -> List[Dict[str, Any]]:
        table_fields: List[str] = ["string", "type", "relation", "help"]

        result: List[Dict[str, Any]] = self.execute_kw(
            model=table_name, method="fields_get", kwargs={"attributes": table_fields}
        )

        return result

    def get_courses(self, teacher_id: int) -> List[CourseOdoo]:
        course_fields: List[str] = [
            "id",
            "name",
            "description",
            "product_id",
        ]
        arguments: List[Union[Tuple[str, str, Any], str, int]] = [
            ("user_id", "=", teacher_id)
        ]

        courses: List[Dict[str, Any]] = self.execute_kw(
            model="slide.channel",
            method="search_read",
            args=[arguments],
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

        arguments: List[Union[Tuple[str, str, Any], str, int]] = [
            ("channel_id", "=", course_id)
        ]

        lessons: List[Dict[str, Any]] = self.execute_kw(
            model="slide.slide",
            method="search_read",
            args=[arguments],
            kwargs={"fields": lesson_fields},
        )

        return [
            LessonOdoo(external_reference=lesson["id"], **lesson) for lesson in lessons
        ]

    def get_course_sales(self, product_id: int) -> List[SaleOdoo]:
        details_sale_fields: List[str] = ["order_id", "price_total", "product_uom_qty"]
        arguments: List[Union[Tuple[str, str, Any], str, int]] = [
            ("product_id", "=", product_id),
            ("order_id.state", "in", ["sale", "done"]),
        ]

        details_sale: List[Dict[str, Any]] = self.execute_kw(
            model="sale.order.line",
            method="search_read",
            args=[arguments],
            kwargs={
                "fields": details_sale_fields,
            },
        )

        order_mapped: Dict[int, List[DetailSaleOdoo]] = {}
        for detail in details_sale:
            order_id: int = detail["order_id"][0]
            detail_sale_odoo: DetailSaleOdoo = DetailSaleOdoo(
                external_reference=order_id,
                price=detail["price_total"],
                quantity=detail["product_uom_qty"],
            )
            if not order_mapped.get(order_id):
                order_mapped[order_id] = [detail_sale_odoo]
            else:
                order_mapped[order_id].append(detail_sale_odoo)

        sale_fields: List[str] = ["id", "date_order", "partner_id"]
        sales_information: List[Dict[str, Any]] = self.execute_kw(
            model="sale.order",
            method="read",
            args=[list(order_mapped.keys())],
            kwargs={"fields": sale_fields},
        )

        student_set: Set[int] = {sale["partner_id"][0] for sale in sales_information}

        students: List[StudentOdoo] = self.get_students(students_ids=student_set)

        student_map: Dict[int, StudentOdoo] = {}
        for student in students:
            student_map[student.external_reference] = student

        sales: List[SaleOdoo] = []
        for sale in sales_information:
            sales.append(
                SaleOdoo(
                    external_reference=sale["id"],
                    date=sale["date_order"],
                    detail_sale=order_mapped[sale["id"]],
                    buyer=student_map[sale["partner_id"][0]],
                )
            )

        return sales

    def get_students_ids(self, course_id: int) -> Set[int]:
        student_fields: List[str] = ["partner_id"]

        arguments: List[Union[Tuple[str, str, Any], str, int]] = [
            ("channel_id", "=", course_id)
        ]

        students: List[Dict[str, Any]] = self.execute_kw(
            model="slide.channel.partner",
            method="search_read",
            args=[arguments],
            kwargs={
                "fields": student_fields,
                "order": "id desc",
            },
        )

        students_ids: Set[int] = {student["partner_id"][0] for student in students}

        return students_ids

    def get_students(self, students_ids: Set[int]) -> List[StudentOdoo]:
        student_fields: List[str] = ["id", "name", "email", "phone"]

        students: List[Dict[str, Any]] = self.execute_kw(
            model="res.partner",
            method="read",
            args=[list(students_ids)],
            kwargs={"fields": student_fields},
        )

        return [
            StudentOdoo(
                external_reference=student["id"],
                phone=student["phone"] if student["phone"] else None,
                emai=student["email"] if "@" in student["email"] else None,
                name=student["name"],
            )
            for student in students
        ]

    def get_teachers_ids(self) -> Set[int]:
        courses: List[Dict[str, Any]] = self.execute_kw(
            model="slide.channel", method="search_read", kwargs={"fields": ["user_id"]}
        )

        teachers_id: Set[int] = {course["user_id"][0] for course in courses}

        return teachers_id

    def get_teachers(self, teachers_ids: Set[int]) -> List[TeacherOdoo]:
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
