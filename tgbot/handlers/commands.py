import logging
from datetime import datetime, timezone

import re
import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bs4 import BeautifulSoup

from aiogram import Router
from aiogram import types
from aiogram.filters import CommandStart, state
from aiogram import F

from tgbot.models.models import Url
import tgbot.database.requests as rq
import tgbot.keyboards.keyboards as kb
from tgbot.llm.llm import predict_category_and_priority

from tgbot.data.config import CATEGORIES_COMMANDS as CATEGORIES
from tgbot.states.states import SearchState
from aiogram.fsm import state

router = Router()

# Регулярное выражение для поиска URL
url_pattern = r'https?://(?:www\.)?[^\s/$.?#].[^\s]*'

# Регулярные выражения для распознавания ссылок соцсетей
SOCIAL_PATTERNS = {
    "facebook": r"(?:https?://)?(?:www\.)?(facebook\.com|fb\.com)",
    "instagram": r"(?:https?://)?(?:www\.)?(instagram\.com)",
    "twitter": r"(?:https?://)?(?:www\.)?(twitter\.com)",
    "linkedin": r"(?:https?://)?(?:www\.)?(linkedin\.com)",
    "youtube": r"(?:https?://)?(?:www\.)?(youtube\.com|youtu\.be)",
    "tiktok": r"(?:https?://)?(?:www\.)?(tiktok\.com)",
    "vk": r"(?:https?://)?(?:www\.)?(vk\.com)",
    "ok": r"(?:https?://)?(?:www\.)?(ok\.ru)",
    "reddit": r"(?:https?://)?(?:www\.)?(reddit\.com)",
    "pinterest": r"(?:https?://)?(?:www\.)?(pinterest\.com)",
    "snapchat": r"(?:https?://)?(?:www\.)?(snapchat\.com)",
}


_message = None
_urls = None


@router.message(CommandStart())
async def start_command_handler(message: types.Message):
    _user = await rq.get_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    greeting_text = f"С возвращением, {_user.full_name}! Чем могу помочь?"
    await message.answer(greeting_text, reply_markup=kb.main)


@router.message(F.text == "Категории")
async def categories(message: types.Message):
    await message.answer(text='Выберите категорию', reply_markup=await kb.categories())


@router.message(F.text == "Приоритеты")
async def priorities(message: types.Message):
    await message.answer(text='Выберите приоритет', reply_markup=await kb.priorities())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию')
    # await callback.answer(callback.data)
    # logging.error(f"comands.category. callback_data={callback.data}")
    await callback.message.answer(text='Выберите url по категории',
                                  reply_markup=await kb.urls_by_category(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('priority_'))
async def priority(callback: CallbackQuery):
    await callback.answer('Вы выбрали приоритет')
    # await callback.answer(callback.data)
    # logging.error(f"comands.category. callback_data={callback.data}")
    await callback.message.answer(text='Выберите url по приоритету',
                                  reply_markup=await kb.urls_by_priority(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith("save_url_"))
async def save_url(callback: CallbackQuery):
    logging.error(f"save_url.callback.data: {callback.data}")
    idx = int(callback.data.split("_")[2])
    if _urls is None or type(_urls) is not list:
        return

    url = _urls[idx]

    user = _user
    title = await __fetch_page_title(url)
    timestamp_utc = int(datetime.now(timezone.utc).timestamp())

    source_info_telegram_forwarded = __get_source_telegram_forwarded(_message)
    source_info_social_network = __get_source_social_network(message=_message)
    logging.error(f"source_info_social_network: {source_info_social_network}")
    logging.error(f"source_info_telegram_forwarded: {source_info_telegram_forwarded}")

    source_info = f"{source_info_telegram_forwarded}\n" if source_info_telegram_forwarded else ""
    source_info += source_info_social_network if source_info_social_network else ""
    source_info = source_info if source_info else "Источник пересылки неизвестен или скрыт."
    logging.error(f"source_info: {source_info}")

    # полученное с помощью LLM атегория и приоритет
    predicted_category, predicted_priority = await predict_category_and_priority(title)

    category = await rq.get_category_by_text(predicted_category)
    priority = await rq.get_priority_by_text(predicted_priority)

    _url = Url()
    _url.user = user.tg_id
    _url.priority = priority.id
    _url.category = category.id
    _url.title = title
    _url.url = url
    _url.source = source_info
    _url.timestamp = timestamp_utc

    await rq.save_url(_url)

    await callback.answer(f"Ссылка сохранена: {url}")


# Обработчик для любых сообщений
@router.message()
async def handle_any_message(message: types.Message):
    global _message
    global _user
    global _urls

    # Найти все URL в тексте
    _urls = re.findall(url_pattern, message.text)
    if not _urls:
        await message.answer("Ссылка не найдена в сообщении.")
        return

    _user = await rq.get_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    _message = message

    # Отправить сообщение с кнопками
    await message.answer("Выберите ссылки для сохранения:", reply_markup=await kb.urls_to_save(_urls))


async def __fetch_page_title(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    # Парсинг HTML с помощью BeautifulSoup
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    title_tag = soup.find('title')
                    return title_tag.text.strip() if title_tag else "Заголовок отсутствует"
                else:
                    return None
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")
        return None


def __get_source_telegram_forwarded(message: types.Message):
    source_info = None

    # Если сообщение переслано от пользователя
    if message.forward_from:
        user = message.forward_from
        source_info = f"Сообщение переслано от пользователя:\n" \
                f"- Имя: {user.full_name}\n" \
                f"- Username: @{user.username}\n" \
                f"- ID: {user.id}"
    elif message.forward_from_chat:  # Если сообщение переслано из канала или группы
        chat = message.forward_from_chat
        source_type = "канала" if chat.type == "channel" else "группы"
        source_info = f"Сообщение переслано из {source_type}:\n" \
                f"- Название: {chat.title}\n" \
                f"- Username: @{chat.username if chat.username else 'отсутствует'}\n" \
                f"- ID: {chat.id}"

    return source_info


def __get_source_social_network(message: types.Message):
    return __detect_social_media_link(text=message.text)


def __detect_social_media_link(text: str):
    for key, category_entry in CATEGORIES.items():
        for entry in category_entry:
            if re.search(entry, text):
                return key

    return None



