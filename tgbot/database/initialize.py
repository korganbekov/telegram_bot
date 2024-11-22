from tgbot.models.models import async_session
from tgbot.models.models import Category, Priority

from sqlalchemy import select

from tgbot.data.config import CATEGORIES, PRIORITIES

async def fill_categories():
    async with async_session() as session:
        category = await session.scalar(select(Category))
        if category:
            return

        for category in CATEGORIES:
            session.add(Category(category=category))
            await session.commit()


async def fill_priorities():
    async with async_session() as session:
        priority = await session.scalar(select(Priority))
        if priority:
            return

        for priority in PRIORITIES:
            session.add(Priority(priority=priority))
            await session.commit()


async def async_main():
    await fill_categories()
    await fill_priorities()