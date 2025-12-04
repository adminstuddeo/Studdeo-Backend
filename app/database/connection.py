from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.configuration import configuration
from app.enums import Environment


class Database:
    def __init__(self) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=configuration.DATABASE_URL.encoded_string(),
            echo=configuration.environment == Environment.DEVELOPMENT,
            pool_size=10,
        )
        self.session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    async def get_async_session(self) -> AsyncGenerator[AsyncSession]:
        async with self.session_maker() as session:
            yield session


database: Database = Database()
