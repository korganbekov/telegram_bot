import logging

from tgbot.database.models import async_session
from tgbot.database.models import User, Category, Url, Priority

from sqlalchemy import select, and_


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_priorities():
    async with async_session() as session:
        return await session.scalars(select(Priority))

async def get_category(id=3):
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.id == id))
        if not category:
            category = await session.scalar(select(Category).where(Category.id == 3))
        return category

async def get_category_by_text(category_text):
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.category == category_text))
        if not category:
            category = await session.scalar(select(Category).where(Category.id == 3))
        return category

async def get_priority(id=3):
    async with async_session() as session:
        priority = await session.scalar(select(Priority).where(Priority.id == id))
        if not priority:
            priority = await session.scalar(select(Category).where(Priority.id == 3))
        return priority

async def get_priority_by_text(priority_text):
    async with async_session() as session:
        priority = await session.scalar(select(Priority).where(Priority.priority == priority_text))
        if not priority:
            priority = await session.scalar(select(Category).where(Priority.id == 3))
        return priority

async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

        return user




async def get_url(id):
    async with async_session() as session:
        return await session.scalar(select(Url).where(Url.id == id))


async def get_urls_by_category(id):
    async with async_session() as session:
        return await session.scalars(select(Url).where(Url.category == id))

async def get_urls_by_priority(id):
    async with async_session() as session:
        return await session.scalars(select(Url).where(Url.priority == id))


async def get_urls(filter):
    # logging.info(f'requests.get_urls({filter})')
    async with async_session() as session:
        conditions = [
            getattr(Url, key) == value
            for key, value in filter.items()
            if value is not None  # Добавляем только те, которые не None
        ]

        query = select(Url).where(and_(*conditions)) if conditions else select(Url)
        result = await session.scalars(query)
        # logging.info(f'requests.get_urls. len(result): {len(result.all())}')
        return result.all()


async def save_url(url: Url):
    logging.warning('save_url')
    try:
        async with (async_session() as session):
            logging.warning('save_url_1')
            logging.info(f"url.id: {url.id}")
            logging.info(f"url.title: {url.title})")
            logging.info(f"url.user {url.user}")
            logging.info(f"url.name: {url.url}")
            logging.info(f"url.source: {url.source}")
            logging.info(f"url.category: {url.category}, ")
            logging.info(f"url.priority: {url.priority}, ")
            logging.info(f"url.timestamp={url.timestamp}")

            session.add(url)
            await session.commit()
            # message = f"url: {url.url}, title: {url.title} is saved to DB"
            # logging.info(message)
            return True
    except Exception as e:
        # message = f"url: {url.url}, title: {url.title} is not saved to DB"
        # logging.error(message)
        return False
