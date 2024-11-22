from sqlalchemy import String, BigInteger, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from tgbot.data import config

engine = create_async_engine(url=config.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[String] = mapped_column(String(50), nullable=True)
    full_name: Mapped[String] = mapped_column(String(100), nullable=True)


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(30), nullable=True)


class Priority(Base):
    __tablename__ = 'priorities'
    id: Mapped[int] = mapped_column(primary_key=True)
    priority: Mapped[str] = mapped_column(String(30), nullable=True)


class Url(Base):
    __tablename__ = 'urls'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=True)
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=True)
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    priority: Mapped[int] = mapped_column(ForeignKey('priorities.id'))
    user: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    timestamp: Mapped[int] = mapped_column(Integer, nullable=True)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

