import re
import aiohttp
from bs4 import BeautifulSoup
from aiogram import types

from tgbot.data.config import CATEGORIES_COMMANDS as CATEGORIES

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
    text = message.text
    for key, category_entry in CATEGORIES.items():
        for entry in category_entry:
            if re.search(entry, text):
                return key

    return None

