import logging
import re
from datetime import datetime, timezone
from typing import List

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

# маджик фильтр
from aiogram import F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.states.states import SearchState
from tgbot.llm.llm import predict_category_and_priority

from tgbot.database import requests
from tgbot.keyboards import keyboards
from tgbot.handlers.helpers import (__get_source_social_network,
                                    __get_source_telegram_forwarded, __fetch_page_title)


from tgbot.models.models import Url

_user = None
_message = None
_urls = None

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



# Клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...", keyboard=[
    [KeyboardButton(text="Категории"), KeyboardButton(text="Приоритеты")],
    # [KeyboardButton(text="Приоритеты")],
    [KeyboardButton(text="Добавление новых данных"), KeyboardButton(text="Поиск данных по тексту")]
])

# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
    _user = await requests.get_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)


################################### РЕАЛИЗАЦИЯ ПОИСКА ПО ТЕКСТУ###############################################
# Обработчик кнопки "Поиск ссылки по тексту"
@router.message(F.text == "Поиск данных по тексту")
async def ask_for_search_query(message: types.Message, state: FSMContext):
    await state.set_state(SearchState.waiting_for_query)
    await message.answer("Введите текст для поиска:")

# Обработчик для ввода текста пользователем
@router.message(SearchState.waiting_for_query)
async def search_database(message: types.Message, state: FSMContext):
    await message.answer("search_database:")
    query = message.text.strip()

    # Здесь ваша логика поиска в БД
    urls: List[Url] = await requests.get_urls_by_text(query)
    await message.answer(f"search_database: len(urls): {len(urls)}")

    if urls:
        result = ""
        for url in urls:
            result += result + url.url + "\n"
        await message.answer(f"Найдено: {result}")
    else:
        await message.answer("Ничего не найдено.")

    # Завершение состояния
    await state.clear()
################################### РЕАЛИЗАЦИЯ ПОИСКА ПО ТЕКСТУ###############################################

################################### ДОБАВЛЕНИЯ НОВЫХ ДАННЫХ###############################################
# Обработчик кнопки "Добавление новых данных"
@router.message(F.text == "Добавление новых данных")
async def ask_for_add_data(message: types.Message, state: FSMContext):
    await state.set_state(SearchState.waiting_for_input_text)
    await message.answer("Введите или вставьте текст:")


# Обработчик для ввода текста пользователем
@router.message(SearchState.waiting_for_input_text)
async def add_data_to_database(message: types.Message, state: FSMContext):
    global _urls
    global _message
    global _user

    await message.answer("add_data_to_database:")

    # Найти все URL в тексте
    _urls = re.findall(url_pattern, message.text)
    if not _urls:
        await message.answer("Ссылка не найдена в сообщении.")
        return

    _user = await requests.get_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    _message = message

    # Отправить сообщение с кнопками
    await message.answer("Выберите ссылки для сохранения:", reply_markup=await keyboards.urls_to_save(_urls))

    # Завершение состояния
    await state.clear()


@router.callback_query(F.data.startswith("save_url_"))
async def save_url(callback: CallbackQuery):
    logging.error(f"save_url.callback.data: {callback.data}")
    idx = int(callback.data.split("_")[2])
    logging.error(f"save_url. idx: {idx}")
    logging.error(f"save_url. len(_urls): {len(_urls)}")

    if _urls is None or type(_urls) is not list:
        return

    url = _urls[idx]

    user = _user
    title = await  __fetch_page_title(url)
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

    category = await requests.get_category_by_text(predicted_category)
    priority = await requests.get_priority_by_text(predicted_priority)

    _url = Url()
    _url.user = user.tg_id
    _url.priority = priority.id
    _url.category = category.id
    _url.title = title
    _url.url = url
    _url.source = source_info
    _url.timestamp = timestamp_utc

    result = await requests.save_url(_url)
    await callback.answer(result)
