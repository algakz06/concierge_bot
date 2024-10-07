from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.configs.settings import settings


class DatabaseSessionManager:
    session: AsyncSession

    def __init__(self):
        self.engine = create_async_engine(
            url=settings.SQLALCHEMY_DATABASE_URI.__str__(),  # type: ignore
            echo=True,
            max_overflow=-1,
        )
        self._session_maker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False
        )

    async def get_session(self):
        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
        finally:
            await session.close()

database_session_manager = DatabaseSessionManager()
