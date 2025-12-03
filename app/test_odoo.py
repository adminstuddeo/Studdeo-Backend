from app.external_services import odoo

content = odoo.execute_kw(
    "slide.channel",
    "search_read",
    [],
    {"fields": ["model", "name"]},
)


with open("app/schemas/examples/modelos.json", "+w") as file:
    file.write(str(content).replace("'", '"'))
