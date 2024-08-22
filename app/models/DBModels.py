from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    ...

class Role(Base):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[int] = mapped_column(ForeignKey("role.id", ondelete="SET NULL"))
    telegram_id: Mapped[str]
    phone_number: Mapped[str]

class Message(Base):
    __tablename__ = "message"

class Subscriptions(Base):
    __tablename__ = "subscriptions"
