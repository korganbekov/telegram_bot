import uuid
import json

import logging
from datetime import datetime, timezone
import copy

import re
import aiohttp
from bs4 import BeautifulSoup

from aiogram import Router
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

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
user = {'id': None, 'tg_id': None, 'name': None, 'full_name': None}

# Регулярное выражение для поиска URL
url_pattern = r'https?://(?:www\.)?[^\s/$.?#].[^\s]*'

@router.message(CommandStart())
async def start_command_handler(message: types.Message, state: FSMContext):
    global user
    user = await __get_user(message=message)

    greeting_text = f"С возвращением, {user['full_name']}! Чем могу помочь?"

    await message.answer(greeting_text)

# Обработчик для любых сообщений
@router.message()
async def handle_any_message(message: types.Message):
    global data
    global user

    if user.get('tg_id') is None:
        user = await __get_user(message=message)

    # Найти все URL в тексте
    urls = re.findall(url_pattern, message.text)
    if not urls:
        await message.answer("Ссылка не найдена в сообщении.")
        return


    titles = []
    for url in urls:
        """
        template_entry = {
    'url':None,
    'title':None,
    'category': None,
    'priority': None,
    'source': None,
    'telegram_user_id': None,
    'timestamp': None
}
        """
        # Получить заголовок страницы
        title = await __fetch_page_title(url)
        titles.append(f"{url} — {title}")

        # Получение текущего времени в UTC
        timestamp_utc = int(datetime.now(timezone.utc).timestamp())
        source_info = await __get_source_info(message=message)

        entry = copy.deepcopy(template_entry)
        entry['guid'] = str(uuid.uuid4())
        entry['url'] = url
        entry['title'] = title
        # entry['source'] = source_info
        entry['source'] = entry['source']
        entry['timestamp'] = timestamp_utc
        entry['telegram_user_id'] = user['tg_id']
        entry['full_name'] = user['full_name']
        entry['category'] = entry['category']
        entry['priority'] = entry['priority']

        # data.append(entry)
        await __save_data(entry=entry)

    with open('result.json', 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile)

    # Ответ пользователю
    # await message.answer("\n".join(titles))
    await message.answer(str(data))


async def __save_data(entry):
    global data
    data.append(entry)
    message = f"url: {entry['url']}, title: {entry['title']} is saved to DB"
    await __log_saved_url(message=message)


async def __fetch_page_title(url: str) -> str:
    try:
        # Асинхронная загрузка страницы
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

async def __get_source_info(message: types.Message):
    if message.forward_from:  # Если сообщение переслано от пользователя
        # user = message.forward_from
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
    else:  # Если информация о пересылке недоступна
        source_info = "Источник пересылки неизвестен или скрыт."

    return source_info

async def __get_user(message: types.Message):
    user = {}
    from_user = message.from_user
    from_user_id = message.from_user.id
    user['guid'] = str(uuid.uuid4())
    user['tg_id'] = from_user_id
    user['name'] = from_user
    user['full_name'] = from_user.full_name
    return user

# Функция для отправки логов в канал
async def __log_saved_url(message: str):
    try:
        logging.info(f"Лог отправлен: {message}")
    except Exception as e:
        logging.error(f"Ошибка отправки лога: {e}")