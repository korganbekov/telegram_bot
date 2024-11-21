from sqlalchemy import String, BigInteger, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from tgbot.data import config

# Create the async engine and session
engine = create_async_engine(url=config.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(30))

class Priority(Base):
    __tablename__ = 'priorities'
    id: Mapped[int] = mapped_column(primary_key=True)
    priority: Mapped[int] = mapped_column(String(30))

class Url(Base):
    __tablename__ = 'urls'
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(100))
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    priority: Mapped[int] = mapped_column(ForeignKey('priority.id'))
    source: Mapped[str] = mapped_column(String(100))
    user: Mapped[int] = mapped_column(ForeignKey('user.tg_id'))
    timestamp: Mapped[int]


async def async_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
