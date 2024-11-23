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


# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
    _user = await requests.get_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    greeting_text = f"С возвращением, {_user.full_name}! Чем могу помочь?"
    await message.answer(greeting_text, reply_markup=keyboards.main)


################################### РЕАЛИЗАЦИЯ ПОИСКА ПО ТЕКСТУ###############################################
# Обработчик кнопки "Поиск ссылки по тексту"
@router.message(F.text == "Поиск данных по тексту")
async def ask_for_search_query(message: types.Message, state: FSMContext):
    await state.set_state(SearchState.waiting_for_query)
    await message.answer("Введите текст для поиска:")

# Обработчик для ввода текста пользователем
@router.message(SearchState.waiting_for_query)
async def search_database(message: types.Message, state: FSMContext):
    query = message.text.strip()

    urls: List[Url] = await requests.get_urls_by_text(query)

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
    if _urls is None or type(_urls) is not list:
        return

    idx = int(callback.data.split("_")[2])
    url = _urls[idx]

    user = _user
    title = await  __fetch_page_title(url)
    timestamp_utc = int(datetime.now(timezone.utc).timestamp())

    source_info_telegram_forwarded = __get_source_telegram_forwarded(_message)
    source_info_social_network = __get_source_social_network(message=_message)

    source_info = f"{source_info_telegram_forwarded}\n" if source_info_telegram_forwarded else ""
    source_info += source_info_social_network if source_info_social_network else ""
    source_info = source_info if source_info else "Источник пересылки неизвестен или скрыт."

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


###############################################################################
@router.message(F.text == "Категории")
async def categories(message: types.Message):
    await message.answer(text='Выберите категорию', reply_markup=await keyboards.categories())


@router.message(F.text == "Приоритеты")
async def priorities(message: types.Message):
    await message.answer(text='Выберите приоритет', reply_markup=await keyboards.priorities())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию')
    await callback.message.answer(text='Выберите url по категории',
                                  reply_markup=await keyboards.urls_by_category(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('priority_'))
async def priority(callback: CallbackQuery):
    await callback.answer('Вы выбрали приоритет')
    await callback.message.answer(text='Выберите url по приоритету',
                                  reply_markup=await keyboards.urls_by_priority(callback.data.split('_')[1]))