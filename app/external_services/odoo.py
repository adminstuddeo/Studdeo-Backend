from typing import Any, Dict, List, Optional, cast
from xmlrpc.client import ServerProxy

from app.configuration import configuration

# TODO: Refactorizar


class OdooClient:
    """
    Cliente XML-RPC para Odoo Community.

    Definición de 'profesor':
    - Usuario responsable de curso (slide.channel.user_id).
    """

    def __init__(
        self,
        url: str = configuration.ODOO_URL.encoded_string(),
        db: str = configuration.ODOO_DB,
        user: str = configuration.ODOO_USER,
        api_key: str = configuration.ODOO_API_KEY.get_secret_value(),
    ) -> None:
        self.url: str = url
        self.db: str = db
        self.user: str = user
        self.api_key: str = api_key

        self.common = ServerProxy(uri=f"{self.url}/xmlrpc/2/common")
        self.models = ServerProxy(uri=f"{self.url}/xmlrpc/2/object")
        self.uid = self.common.authenticate(self.db, self.user, self.api_key, {})
        if not self.uid:
            raise ValueError(
                "No se pudo autenticar en Odoo. Verifica DB, usuario y API key."
            )

    def authenticate(self):
        try:
            uuid = self.common.authenticate(self.db, self.user, self.api_key)

            self.uid = cast(str, uuid)

        except Exception as auth_error:
            raise auth_error

    # ---------- Util ----------
    def execute_kw(
        self, model: str, method: str, args: list, kwargs: Optional[dict] = None
    ):
        return self.models.execute_kw(
            self.db, self.uid, self.api_key, model, method, args, kwargs or {}
        )

    # ---------- Profesores ----------
    def get_professor_user_ids(self) -> List[int]:
        """IDs únicos de usuarios responsables de al menos un curso (slide.channel.user_id)."""
        channels = self.execute_kw(
            "slide.channel", "search_read", [[]], {"fields": ["user_id"], "limit": 0}
        )
        ids = {rec["user_id"][0] for rec in channels if rec.get("user_id")}
        return list(ids)

    def list_professors(self) -> List[Dict[str, Any]]:
        ids = self.get_professor_user_ids()
        if not ids:
            return []
        users = self.execute_kw(
            "res.users",
            "read",
            [ids],
            {"fields": ["id", "name", "login", "email", "active"]},
        )
        users.sort(key=lambda u: (u.get("name") or "").lower())
        return users

    # ---------- Helpers: lecciones ----------
    def _course_lessons(self, channel_id: int, limit: int = 50) -> Dict[str, Any]:
        try:
            slides = self.execute_kw(
                "slide.slide",
                "search_read",
                [[("channel_id", "=", channel_id)]],
                {"fields": ["id", "name", "slide_type", "category_id"], "limit": limit},
            )
            return {
                "count": self.execute_kw(
                    "slide.slide", "search_count", [[("channel_id", "=", channel_id)]]
                ),
                "items": slides,
            }
        except Exception:
            return {"count": 0, "items": []}

    # ---------- Helpers: ventas + compradores ----------
    def _course_sales(self, channel: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ventas del curso si está vinculado a un producto (website_slides_sale).
        Además de totales, devuelve:
          - buyers: lista de compradores con partner/email
          - buyers_by_partner: {partner_id: email}
        """
        try:
            product = channel.get("product_id")
            if not product:
                return {
                    "has_product": False,
                    "product_id": None,
                    "orders": 0,
                    "units": 0.0,
                    "revenue": 0.0,
                    "buyers": [],
                    "buyers_by_partner": {},
                }

            product_id = product[0] if isinstance(product, list) else product
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
            return {
                "has_product": False,
                "product_id": None,
                "orders": 0,
                "units": 0.0,
                "revenue": 0.0,
                "buyers": [],
                "buyers_by_partner": {},
            }

    # ---------- Helpers: inscritos (con fallback a compradores) ----------
    def _course_attendees(
        self,
        channel_id: int,
        limit: int = 50,
        buyers_by_partner: Optional[Dict[int, str]] = None,
    ) -> Dict[str, Any]:
        """
        Inscritos a un curso (slide.channel.partner).
        Devuelve: total, y lista con id/nombre/email/completed.
        Si el partner no tiene email, usa buyers_by_partner[partner_id] (correo de la compra).
        """
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
            return {
                "count": 0,
                "summary": "0 alumnos inscritos",
                "students": [],
                "error": str(e),
            }

    # ---------- Detalle del profesor ----------
    def professor_detail(
        self, user_id: int, attendees_limit: int = 50, lessons_limit: int = 50
    ) -> Dict[str, Any]:
        user_rec = self.execute_kw(
            "res.users",
            "read",
            [[user_id]],
            {"fields": ["id", "name", "login", "email", "active"]},
        )
        user = user_rec[0] if user_rec else {}

        course_fields = [
            "id",
            "name",
            "description",
            "website_published",
            "user_id",
            "product_id",
        ]
        channels = self.execute_kw(
            "slide.channel",
            "search_read",
            [[("user_id", "=", user_id)]],
            {"fields": course_fields, "limit": 0, "order": "id desc"},
        )

        detailed = []
        total_students = 0

        for ch in channels:
            ch_id = ch["id"]
            # 1) ventas (para tener buyers_by_partner)
            sales = self._course_sales(ch)
            buyers_by_partner = sales.get("buyers_by_partner", {})

            # 2) inscritos con fallback a correos de ventas
            attendees = self._course_attendees(
                ch_id, limit=attendees_limit, buyers_by_partner=buyers_by_partner
            )

            # 3) lecciones
            lessons = self._course_lessons(ch_id, limit=lessons_limit)

            total_students += attendees["count"]

            detailed.append(
                {
                    "id": ch_id,
                    "name": ch.get("name"),
                    "website_published": ch.get("website_published", False),
                    "description": ch.get("description"),
                    "responsable": ch.get("user_id")[1] if ch.get("user_id") else None,
                    "inscritos": attendees["count"],
                    "inscritos_detalle": attendees[
                        "students"
                    ],  # con email de partner o de compra
                    "lessons": lessons,
                    "sales": {
                        "has_product": sales["has_product"],
                        "product_id": sales["product_id"],
                        "orders": sales["orders"],
                        "units": sales["units"],
                        "revenue": sales["revenue"],
                        "buyers": sales[
                            "buyers"
                        ],  # lista de compradores (por si quieres auditar)
                    },
                }
            )

        return {
            "user": user,
            "courses": {
                "count": len(channels),
                "total_students": total_students,
                "items": detailed,
            },
        }


odoo: OdooClient = OdooClient()
