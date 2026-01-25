from dataclasses import dataclass
from datetime import datetime
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
    _uid: Optional[int] = None

    def get_uid(self) -> int:
        if self._uid is None:
            common: ServerProxy = ServerProxy(
                uri=f"{self.url}/xmlrpc/2/common", allow_none=True
            )
            self._uid = cast(
                int, common.authenticate(self.db, self.user, self.api_key, {})
            )

        return self._uid

    def execute_kw(
        self,
        model: str,
        method: str,
        args: List[List[Union[str, int, Tuple[str, str, Any]]]] = [],
        kwargs: Optional[dict[str, Union[List[str], str, int]]] = None,
    ) -> List[Dict[str, Any]]:
        uid: int = self.get_uid()

        models: ServerProxy = ServerProxy(
            uri=f"{self.url}/xmlrpc/2/object", allow_none=True
        )

        response: List[Dict[str, Any]] = cast(
            List[Dict[str, Any]],
            models.execute_kw(self.db, uid, self.api_key, model, method, args, kwargs),
        )

        return response

    def _get_database_information(self) -> List[Dict[str, Any]]:
        database_fields: List[str] = ["model", "name", "relation", "help"]

        result: List[Dict[str, Any]] = self.execute_kw(
            model="ir.model", method="search_read", kwargs={"fields": database_fields}
        )

        return result

    def _get_table_information(self, table_name: str) -> List[Dict[str, Any]]:
        table_fields: List[str] = ["string", "type", "relation", "help"]

        result: List[Dict[str, Any]] = self.execute_kw(
            model=table_name, method="fields_get", kwargs={"attributes": table_fields}
        )

        return result

    def get_all_courses(self, date_from: Optional[datetime] = None) -> List[CourseOdoo]:
        course_fields: List[str] = [
            "id",
            "name",
            "description",
            "product_id",
            "user_id",
            "website_default_background_image_url",
            "create_date",
        ]

        arguments: List[Union[Tuple[str, str, Any], str, int]] = []

        if date_from:
            arguments.append(("create_date", ">=", date_from))

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
                user_id=course["user_id"][0],
                create_date=course["create_date"],
                image=configuration.ODOO_URL.encoded_string()
                + course["website_default_background_image_url"],
            )
            for course in courses
        ]

    def get_courses(self, teacher_id: int) -> List[CourseOdoo]:
        course_fields: List[str] = [
            "id",
            "name",
            "description",
            "product_id",
            "website_default_background_image_url",
            "create_date",
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
                user_id=teacher_id,
                create_date=course["create_date"],
                image=configuration.ODOO_URL.encoded_string()
                + course["website_default_background_image_url"],
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

    def get_course_sales(self, product_id: int, discount: float) -> List[SaleOdoo]:
        details_sale_fields: List[str] = [
            "order_id",
            "price_total",
            "product_uom_qty",
        ]
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

        sale_fields: List[str] = [
            "id",
            "date_order",
            "amount_total",
            "reward_amount",
        ]
        sales_information: List[Dict[str, Any]] = self.execute_kw(
            model="sale.order",
            method="search_read",
            args=[[("id", "in", list(order_mapped.keys()))]],
            kwargs={"fields": sale_fields, "order": "date_order asc"},
        )

        sales: List[SaleOdoo] = []

        for sale in sales_information:
            sales.append(
                SaleOdoo(
                    external_reference=sale["id"],
                    date=sale["date_order"],
                    details_sale=order_mapped[sale["id"]],
                    discount=sale["reward_amount"],
                    total=sale["amount_total"],
                    contract_discount=discount,
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
        student_fields: List[str] = ["id", "name", "email"]

        students: List[Dict[str, Any]] = self.execute_kw(
            model="res.partner",
            method="read",
            args=[list(students_ids)],
            kwargs={"fields": student_fields},
        )

        return [
            StudentOdoo(
                external_reference=student["id"],
                email=student["email"] if "@" in student["email"] else None,
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

        list_teachers: List[TeacherOdoo] = []

        for teacher in teachers:
            name: str = teacher["name"]
            lastname: str = ""

            if len(teacher["name"].split()) != 1:
                name = teacher["name"].split()[0]
                lastname = teacher["name"].split()[1]

            list_teachers.append(
                TeacherOdoo(
                    external_reference=teacher["id"],
                    name=name,
                    lastname=lastname,
                    active=teacher["active"],
                    email=teacher["email"],
                )
            )

        return list_teachers

    def get_teacher_by_email(self, email: str) -> Optional[TeacherOdoo]:
        teacher_fields: List[str] = ["id", "name", "email", "active"]

        teacher: List[Dict[str, Any]] = self.execute_kw(
            model="res.users",
            method="search_read",
            args=[[("email", "=", email)]],
            kwargs={"fields": teacher_fields, "limit": 1},
        )

        if not teacher:
            return None

        name: str = teacher[0]["name"]
        lastname: str = ""

        if len(name.split()) != 1:
            name = teacher[0]["name"].split()[0]
            lastname = teacher[0]["name"].split()[1]

        return TeacherOdoo(
            external_reference=teacher[0]["id"],
            name=name,
            lastname=lastname,
            email=teacher[0]["email"],
            active=teacher[0]["active"],
        )
