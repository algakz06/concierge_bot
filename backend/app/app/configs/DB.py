from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.configs.Settings import settings

Engine = create_engine(
    url=settings.SQLALCHEMY_DATABASE_URI.__str__(),  # type: ignore
    echo=True,
)

SessionLocal = sessionmaker(
    bind=Engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = scoped_session(SessionLocal)
    try:
        yield db
    finally:
        db.close()
