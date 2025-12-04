from typing import Any, Dict, List

from app.external_services.odoo import odoo

"""content: List[Dict[str, Any]] = odoo.execute_kw(
    "res.partner",
    "fields_get",
    [],
    {"attributes": ["string", "type", "relation", "help"]},
)

with open("app/external_services/odoo/documentation/partner.json", "+w") as file:
    file.write(str(content).replace("'", '"'))
"""

profesores = odoo.get_teachers()

student_fields: List[str] = ["partner_id"]


for profesor in profesores:
    courses = odoo.get_courses(profesor.external_reference)
    for course in courses:
        if course.product_id:
            sales = odoo.get_course_sales(product_id=course.product_id)

        students_ids: List[Dict[str, Any]] = odoo.execute_kw(
            model="slide.channel.partner",
            method="search_read",
            args=[[("channel_id", "=", course.external_reference)]],
            kwargs={
                "fields": student_fields,
                "order": "id asc",
            },
        )


"""
 # ---------- Helpers: ventas + compradores ----------
    def _course_sales(self, product_id: int) -> Dict[str, Any]:
        try:
            # Traer líneas de venta del producto en órdenes confirmadas/entregadas
            lines = self.execute_kw(
                "sale.order.line",
                "search_read",
                [
                    [
                        ("product_id", "=", product_id),
                        ("order_id.state", "in", ["sale", "done"]),
                    ]
                ],
                {"fields": ["order_id", "price_total", "product_uom_qty"], "limit": 0},
            )

            order_ids = list(
                {line["order_id"][0] for line in lines if line.get("order_id")}
            )
            units = sum(line.get("product_uom_qty", 0.0) for line in lines)
            revenue = sum(line.get("price_total", 0.0) for line in lines)

            buyers: List[Dict[str, Any]] = []
            buyers_by_partner: Dict[int, str] = {}

            if order_ids:
                orders = self.execute_kw(
                    "sale.order",
                    "read",
                    [order_ids],
                    {"fields": ["id", "name", "state", "date_order", "partner_id"]},
                )
                partner_ids = [
                    o["partner_id"][0] for o in orders if o.get("partner_id")
                ]
                partners_map = {}
                if partner_ids:
                    partners = self.execute_kw(
                        "res.partner",
                        "read",
                        [list(set(partner_ids))],
                        {"fields": ["id", "name", "email", "email_normalized"]},
                    )
                    partners_map = {p["id"]: p for p in partners}

                for o in orders:
                    if not o.get("partner_id"):
                        continue
                    pid, pname = o["partner_id"][0], o["partner_id"][1]
                    p = partners_map.get(pid, {"id": pid, "name": pname})
                    email = p.get("email") or p.get("email_normalized")
                    buyers.append(
                        {
                            "order_id": o["id"],
                            "order_name": o.get("name"),
                            "state": o.get("state"),
                            "date_order": o.get("date_order"),
                            "partner_id": pid,
                            "partner_name": p.get("name") or pname,
                            "email": email,
                        }
                    )
                    if email:
                        buyers_by_partner[pid] = email

            return {
                "has_product": True,
                "product_id": product_id,
                "orders": len(order_ids),
                "units": units,
                "revenue": revenue,
                "buyers": buyers,
                "buyers_by_partner": buyers_by_partner,
            }
        except Exception:
            raise

    # ---------- Helpers: inscritos (con fallback a compradores) ----------
    def _course_attendees(
        self,
        channel_id: int,
        limit: int = 50,
        buyers_by_partner: Optional[Dict[int, str]] = None,
    ) -> Dict[str, Any]:
        buyers_by_partner = buyers_by_partner or {}
        try:
            enrolls = self.execute_kw(
                "slide.channel.partner",
                "search_read",
                [[("channel_id", "=", channel_id)]],
                {
                    "fields": ["partner_id", "completed"],
                    "limit": limit,
                    "order": "id desc",
                },
            )

            attendees: List[Dict[str, Any]] = []
            partner_ids = [e["partner_id"][0] for e in enrolls if e.get("partner_id")]
            partners_map: Dict[int, Dict[str, Any]] = {}

            if partner_ids:
                partners = self.execute_kw(
                    "res.partner",
                    "read",
                    [list(set(partner_ids))],
                    {
                        "fields": [
                            "id",
                            "name",
                            "email",
                            "email_normalized",
                            "phone",
                            "mobile",
                        ]
                    },
                )
                partners_map = {p["id"]: p for p in partners}

            for e in enrolls:
                if not e.get("partner_id"):
                    continue
                pid, pname = e["partner_id"][0], e["partner_id"][1]
                p = partners_map.get(pid, {"id": pid, "name": pname})
                email = (
                    p.get("email")
                    or p.get("email_normalized")
                    or buyers_by_partner.get(pid)
                )

                attendees.append(
                    {
                        "id": p["id"],
                        "name": p.get("name") or pname,
                        "email": email,  # ← ahora con fallback desde órdenes
                        "phone": p.get("phone"),
                        "mobile": p.get("mobile"),
                        "completed": e.get("completed", False),
                    }
                )

            total = self.execute_kw(
                "slide.channel.partner",
                "search_count",
                [[("channel_id", "=", channel_id)]],
            )

            return {
                "count": total,
                "summary": f"{total} alumno(s) inscrito(s)",
                "students": attendees,
            }

        except Exception as e:
            raise
"""
