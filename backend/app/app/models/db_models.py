import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    telegram_id: Mapped[str] = mapped_column(unique=True)
    telegram_username: Mapped[str]
    localization: Mapped[str]
    phone_number: Mapped[str]
    balance: Mapped[float] = mapped_column(default=0)


class Request(Base):
    __tablename__ = "request"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    theme: Mapped[str]
    status: Mapped[str] = mapped_column(default="opened")
    details: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now()
    )


class Item(Base):
    __tablename__ = "item"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("request.id"))
    category: Mapped[str]
    description: Mapped[str]
    price: Mapped[str]


class Image(Base):
    __tablename__ = "image"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"))
    telegram_file_id: Mapped[str]


class Message(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("request.id"))
    question: Mapped[str]
    content: Mapped[str]
    sent_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())


class Subscription(Base):
    __tablename__ = "subscription"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    started_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now()
    )
    end_at: Mapped[datetime.datetime]
    token_quantity: Mapped[int] = mapped_column(default=0)
