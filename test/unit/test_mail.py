from app.repositories import OdooRepository

odoo = OdooRepository()


sales = odoo.get_course_sales(7)

print(sales)
