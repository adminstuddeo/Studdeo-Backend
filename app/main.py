from typing import List

import logfire
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.configuration import configuration
from app.enums import Environment
from app.routes import auth_router, course_router, teacher_router, user_router

routers: List[APIRouter] = [auth_router, course_router, teacher_router, user_router]

app = FastAPI(
    title="Studdeo Odoo API",
    docs_url="/docs" if configuration.environment == Environment.DEVELOPMENT else None,
)

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=[configuration.FRONTEND_URL.encoded_string()],
    allow_methods=["*"],
    allow_headers=["*"],
)

if configuration.environment == Environment.PRODUCTION:
    app.add_middleware(HTTPSRedirectMiddleware)


@app.get("/ping", tags=["Root"])
def ping() -> dict[str, bool]:
    return {"ok": True}


for route in routers:
    app.include_router(router=route)

logfire.configure()
logfire.instrument_fastapi(app=app)

# TODO:
# 2. Ver el tema de las ventas
# 3. Metricas
# 5. Ver como poblar la BD
