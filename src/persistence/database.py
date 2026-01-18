from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


class DBManager:
    def __init__(self, db_path: str):
        self.db_url = f"sqlite+aiosqlite:///{db_path}"
        self.engine = create_async_engine(self.db_url)
        self.session_maker = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
