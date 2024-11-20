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


class SocialNetwork(Base):
    __tablename__ = 'social_networks'
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String[100])


class Url(Base):
    __tablename__ = 'urls'
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String(25))
    user: Mapped[int] = mapped_column(ForeignKey('user.id'))


async def async_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
