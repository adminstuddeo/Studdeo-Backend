from .administrator_http import administrator_router
from .auth_http import auth_router
from .course_http import course_router
from .role_http import role_router
from .sale_http import sale_router
from .teacher_http import teacher_router
from .user_http import user_router

__all__: list[str] = [
    "administrator_router",
    "auth_router",
    "course_router",
    "sale_router",
    "teacher_router",
    "user_router",
    "role_router",
]
