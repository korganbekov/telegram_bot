import asyncio
import logging

import betterlogging as bl
import orjson
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot import handlers
from tgbot.data import config
from tgbot.models.models import async_main as models_async_main
from tgbot.database.initialize import async_main as init_async_main
from tgbot.handlers.commands import router


def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(handlers.setup())


def setup_middlewares(dp: Dispatcher) -> None:
    pass


async def setup_aiogram(dp: Dispatcher) -> None:
    setup_handlers(dp)
    setup_middlewares(dp)


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_aiogram(dispatcher)


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.session.close()
    await dispatcher.storage.close()


async def main():
    setup_logging()

    # создание таблиц
    await models_async_main()
    # нициализация справочников
    await init_async_main()

    session = AiohttpSession(
        json_loads=orjson.loads,
    )

    bot = Bot(
        token=config.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    storage = MemoryStorage()

    dp = Dispatcher(
        storage=storage,
    )
    dp.include_router(router=router)
    dp.startup.register(aiogram_on_startup_polling)
    dp.shutdown.register(aiogram_on_shutdown_polling)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")