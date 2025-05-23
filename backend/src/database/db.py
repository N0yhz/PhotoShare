import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from typing import AsyncGenerator

from src.conf.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine, class_=AsyncSession)

    @contextlib.asynccontextmanager
    async def session(self): 
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmanager.session() as session:
        yield session