from typing import List

import logfire
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configuration import configuration
from app.enums import Environment
from app.routes import (
    auth_router,
    course_router,
    sale_router,
    teacher_router,
    user_router,
)

routers: List[APIRouter] = [
    auth_router,
    course_router,
    sale_router,
    teacher_router,
    user_router,
]

app: FastAPI = FastAPI(
    title="Studdeo Odoo API",
    docs_url="/docs" if configuration.environment == Environment.DEVELOPMENT else None,
)

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=[configuration.FRONTEND_URL.encoded_string().rstrip("/")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", tags=["Root"])
def ping() -> dict[str, str]:
    return {"message": "pong"}


for route in routers:
    app.include_router(router=route)

logfire.configure()
logfire.instrument_fastapi(app=app)
#
