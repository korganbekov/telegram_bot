import logging
from typing import List

from tgbot.models.models import async_session
from tgbot.models.models import User, Category, Url, Priority

from sqlalchemy import select


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_priorities():
    async with async_session() as session:
        return await session.scalars(select(Priority))


async def get_category_by_text(category_text):
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.category == category_text))

        if not category:
            session.add(Category(category=category_text))
            await session.commit()
            category = await session.scalar(select(Category).where(Category.category == category_text))

        return category


async def get_priority_by_text(priority_text):
    async with async_session() as session:
        priority = await session.scalar(select(Priority).where(Priority.priority == priority_text))

        if not priority:
            session.add(Priority(priority=priority_text))
            await session.commit()
            priority = await session.scalar(select(Priority).where(Priority.priority == priority_text))

        return priority


async def get_user(tg_id, name="", full_name=""):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, name=name, full_name=full_name))
            await session.commit()
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

        return user


async def get_urls_by_category(category_id):
    async with async_session() as session:
        return await session.scalars(select(Url).where(Url.category == category_id))


async def get_urls_by_priority(priority_id):
    async with async_session() as session:
        return await session.scalars(select(Url).where(Url.priority == priority_id))


async def save_url(url: Url):
    msg = f"url: {url.url}, title: {url.title} is"
    try:
        async with (async_session() as session):
            session.add(url)
            await session.commit()

            logging.warning(f"{msg} saved to BD")
            return True
    except Exception as e:
        logging.error(f"{msg} not saved to DB")
        return False


async def get_urls_by_text(text) -> List[Url]:
    async with async_session() as session:
        result = await session.scalars(select(Url).where(Url.url.contains(text)))
        return list(result)
