# import os
# import contextlib
# from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
# from src.entity.models import Base
# from dotenv import load_dotenv
# from typing import AsyncGenerator

# load_dotenv()

# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# @contextlib.asynccontextmanager
# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with SessionLocal() as db:  
#         try: 
#             yield db
#         finally:
#             await db.close()

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