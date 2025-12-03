from typing import List

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.configuration import configuration
from app.enums import Environment
from app.routes import auth_router, course_router, teacher_router, user_router

app = FastAPI(
    title="Studdeo Odoo API",
    docs_url="/docs" if configuration.environment == Environment.DEVELOPMENT else None,
)

routers: List[APIRouter] = [auth_router, course_router, teacher_router, user_router]

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=configuration.allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

if configuration.environment == Environment.PRODUCTION:
    app.add_middleware(HTTPSRedirectMiddleware)


@app.get("/ping", tags=["Root"])
def ping() -> dict[str, bool]:
    return {"ok": True}


for route in routers:
    app.include_router(route)

# 2. Enviar el mail al crear el usuario
# 3. Ver el tema de las ventas
# 4. Metricas
# 5. Agregar a la respuesta del courso sus estudiantes
# 6. Ver como poblar la BD
