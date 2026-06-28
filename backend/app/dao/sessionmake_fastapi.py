from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from dao.database import async_session_maker


class DatabaseSession:
    @staticmethod
    async def get_session(commit: bool = False) -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            try:
                yield session

                if commit:
                    await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.aclose()
    
    @staticmethod
    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        async for session in DatabaseSession.get_session(False):
            yield session
    
    @staticmethod
    async def get_db_with_commit() -> AsyncGenerator[AsyncSession, None]:
        async for session in DatabaseSession.get_session(True):
            yield session