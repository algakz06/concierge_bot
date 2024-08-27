import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.configs.DB import Engine

class Base(DeclarativeBase): ...

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    telegram_id: Mapped[int] = mapped_column(unique=True)
    lang: Mapped[str]
    phone_number: Mapped[str]
    sex: Mapped[str]


class Request(Base):
    __tablename__ = "request"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    theme: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now()
    )


class Message(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str]
    sender: Mapped[int] = mapped_column(ForeignKey("user.id"))
    receiver: Mapped[int] = mapped_column(ForeignKey("user.id"))
    sent_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())


class Subscriptions(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    started_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now()
    )
    end_at: Mapped[datetime.datetime]


def init() -> None:
    Base.metadata.create_all(Engine)
