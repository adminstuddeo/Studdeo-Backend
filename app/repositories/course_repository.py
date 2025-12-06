from abc import ABC, abstractmethod
from typing import Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Course


class InterfaceCourseRepository(ABC):
    @abstractmethod
    async def get_course(self, id_course: UUID) -> Optional[Course]: ...

    @abstractmethod
    async def get_courses(self, id_user: UUID) -> Sequence[Course]: ...


class CourseRepository(InterfaceCourseRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self.async_session: AsyncSession = db_session

    async def get_course(self, id_course: UUID) -> Optional[Course]:
        return await self.async_session.get(Course, id_course)

    async def get_courses(self, id_user: UUID) -> Sequence[Course]:
        statement: Select[Tuple[Course]] = select(Course).where(
            Course.id_user == id_user
        )

        result: Result[Tuple[Course]] = await self.async_session.execute(
            statement=statement
        )

        return result.scalars().fetchall()

    async def buil(self): ...
