from typing import List

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
# маджик фильтр
from aiogram import F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.states.states import SearchState

from tgbot.database import requests

from tgbot.models.models import Url

router = Router()

# Клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...", keyboard=[
    [KeyboardButton(text="Категории")],
    [KeyboardButton(text="Приоритеты")],
    [KeyboardButton(text="Поиск ссылки по тексту")]
])

# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)

# Обработчик кнопки "Поиск ссылки по тексту"
@router.message(F.text == "Поиск ссылки по тексту")
async def ask_for_search_query(message: types.Message, state: FSMContext):
    await message.answer("Введите текст для поиска:")
    await state.set_state(SearchState.waiting_for_query)

# Обработчик для ввода текста пользователем
@router.message(StateFilter(SearchState.waiting_for_query))
async def search_database(message: types.Message, state: FSMContext):
    query = message.text.strip()
    # await message.answer(f"Вы ввели: {query}")
    await message.answer("search_database:")
    # Здесь ваша логика поиска в БД
    urls: List[Url] = await requests.get_urls_by_text(query)
    await message.answer(f"search_database: len(urls): {len(urls)}")
    result = ""
    if urls:
        for url in urls:
            result += result + url.url + "\n"
        await message.answer(f"Найдено: {result}")
    else:
        await message.answer("Ничего не найдено.")

    # Завершение состояния
    await state.clear()
