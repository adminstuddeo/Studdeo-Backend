from .auth_http import auth_router
from .course_http import course_router
from .teacher_http import teacher_router
from .user_http import user_router

__all__: list[str] = ["auth_router", "course_router", "teacher_router", "user_router"]
