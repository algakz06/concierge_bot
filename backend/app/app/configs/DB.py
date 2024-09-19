from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import scoped_session, sessionmaker

from app.configs.settings import settings


class DatabaseSessionManager:
    session: AsyncSession

    def __init__(self):
        self.engine = create_async_engine(
            url=settings.SQLALCHEMY_DATABASE_URI.__str__(),  # type: ignore
            echo=True,
            max_overflow=-1,
        )
        self.session_maker = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    def get_session(self):
        return scoped_session(self.session_maker)


database_session_manager = DatabaseSessionManager()
