import uuid
import json

import logging
from datetime import datetime, timezone
import copy

import re
import aiohttp
from aiogram.types import CallbackQuery
from bs4 import BeautifulSoup

from aiogram import Router
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import F

from tgbot.database.models import Url
import tgbot.database.requests as rq
import tgbot.keyboards.keyboards as kb


router = Router()


template_entry = {
    'url':None,
    'title':None,
    'category': None,
    'priority': None,
    'source': None,
    'telegram_user_id': None,
    'timestamp': None
}
data = []
# user = {'id': None, 'tg_id': None, 'name': None, 'full_name': None}

# Регулярное выражение для поиска URL
url_pattern = r'https?://(?:www\.)?[^\s/$.?#].[^\s]*'

# Регулярные выражения для распознавания ссылок соцсетей
SOCIAL_MEDIA_PATTERNS = {
    "YouTube": r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
    "Instagram": r"(https?://)?(www\.)?instagram\.com/",
    "Twitter": r"(https?://)?(www\.)?twitter\.com/",
    "Facebook": r"(https?://)?(www\.)?facebook\.com/",
    "TikTok": r"(https?://)?(www\.)?tiktok\.com/",
    "VK": r"(https?://)?(www\.)?vk\.com/",
    "Telegram": r"(https?://)?(t\.me|telegram\.me)/"
}

# Словарь категорий и соответствующих паттернов
CATEGORIES = {
    "Социальные сети": [r"instagram\.com", r"facebook\.com", r"twitter\.com", r"tiktok\.com", r"vk\.*"],
    "Видео": [r"youtube\.com", r"vimeo\.com", r"twitch\.tv"],
    "Новостные сайты": [r"bbc\.com", r"cnn\.com"],
    "Интернет-магазины": [r"amazon\.com", r"ebay\.com", r"wildberries\.ru"],
    "Образование": [r"coursera\.org", r"wikipedia\.org", r"udemy\.com"],
    "Файловые хранилища": [r"drive\.google\.com", r"dropbox\.com", r"yadi\.sk"],
    "Почта": [r"gmail\.com", r"mail\.ru", r"hotmail\.*"],
}


@router.message(CommandStart())
async def start_command_handler(message: types.Message, state: FSMContext):
    user = await __get_user(message=message)
    greeting_text = f"С возвращением, {user.name}! Чем могу помочь?"
    await message.answer(greeting_text, reply_markup=kb.main)


@router.message(F.text == "Категории")
async def categories(message: types.Message):
    await message.answer(text='Выберите категорию', reply_markup=await kb.categories())

@router.message(F.text == "Приоритеты")
async def categories(message: types.Message):
    await message.answer(text='Выберите приоритет', reply_markup=await kb.priorities())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию')
    await callback.answer(callback.data)
    logging.error(f"comands.category. callback_data={callback.data}")
    await callback.message.answer(text='Выберите url по категории',
                                  reply_markup=await kb.urls_by_category(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('priority_'))
async def priority(callback: CallbackQuery):
    await callback.answer('Вы выбрали приоритет')
    await callback.answer(callback.data)
    logging.error(f"comands.category. callback_data={callback.data}")
    await callback.message.answer(text='Выберите url по приоритету',
                                  reply_markup=await kb.urls_by_priority(callback.data.split('_')[1]))


# Обработчик для любых сообщений
@router.message()
async def handle_any_message(message: types.Message):
    # Найти все URL в тексте
    urls = re.findall(url_pattern, message.text)
    if not urls:
        await message.answer("Ссылка не найдена в сообщении.")
        return

    user = await __get_user(message=message)

    titles = []
    for url in urls:
        # Получить заголовок страницы
        title = await __fetch_page_title(url)
        titles.append(f"{url} — {title}")

        # Получение текущего времени в UTC
        timestamp_utc = int(datetime.now(timezone.utc).timestamp())
        source_info, category, proirity = await __get_source_info_category_priority(message=message)

        entry = copy.deepcopy(template_entry)
        entry['guid'] = str(uuid.uuid4())
        entry['url'] = url
        entry['title'] = title
        entry['source'] = source_info
        entry['timestamp'] = timestamp_utc
        entry['tg_id'] = user.tg_id
        entry['user_name'] = user.name
        entry['category'] = category
        entry['priority'] = proirity

        _url = Url()
        _url.user = user.tg_id
        _url.priority = proirity
        _url.category = category
        _url.title = title
        _url.url = url
        _url.source = source_info
        _url.timestamp = timestamp_utc

        await __save_data(_url, entry)

    with open('result.json', 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile)

    await message.answer(str(data))


async def __save_data(url, entry):
    global data
    try:
        await rq.save_url(url)
        message = f"url: {entry['url']}, title: {entry['title']} is saved to DB"
        logging.info(message)
        data.append(entry)
    except Exception as e:
        message = f"url: {entry['url']}, title: {entry['title']} is not saved to DB"
        logging.error(message)

    return data

async def __fetch_page_title(url: str) -> str:
    try:
        # Асинхронная загрузка страницы
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                logging.error(f"url: {url}, response.status: {response.status}")
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

async def __get_source_info_category_priority(message: types.Message):
    if message.forward_from:  # Если сообщение переслано от пользователя
        user = message.forward_from
        source_info = f"Сообщение переслано от пользователя:\n" \
                f"- Имя: {user.full_name}\n" \
                f"- Username: @{user.username}\n" \
                f"- ID: {user.id}"
        category = await rq.get_category(1)
        priority = await rq.get_priority(1)
    elif message.forward_from_chat:  # Если сообщение переслано из канала или группы
        chat = message.forward_from_chat
        source_type = "канала" if chat.type == "channel" else "группы"
        source_info = f"Сообщение переслано из {source_type}:\n" \
                f"- Название: {chat.title}\n" \
                f"- Username: @{chat.username if chat.username else 'отсутствует'}\n" \
                f"- ID: {chat.id}"
        category = await rq.get_category(1)
        priority = await rq.get_priority(1)
    else:
        social_network_type = __detect_social_media_link(text=message.text)
        if social_network_type:
            source_info = f"{social_network_type}"
            category = await rq.get_category(2)
            priority = await rq.get_priority(2)

        else:  # Если информация о пересылке недоступна
            source_info = "Источник пересылки неизвестен или скрыт."
            category = await rq.get_category(3)
            priority = await rq.get_priority(3)
    return source_info, category.id, priority.id

def __detect_social_media_link(text: str):
    for key, category_entry in CATEGORIES.items():
        for entry in category_entry:
            if re.search(entry, text):
                return key
    return None

async def __get_user(message: types.Message):
    user = await rq.get_user(message.from_user.id)
    name = user.name
    logging.info(name)
    return user
