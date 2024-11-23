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
    [KeyboardButton(text="Категории"), KeyboardButton(text="Приоритеты")],
    # [KeyboardButton(text="Приоритеты")],
    [KeyboardButton(text="Добавление новых данных"), KeyboardButton(text="Поиск данных по тексту")]
])

# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
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
    # await state.clear()
    await message.answer("search_database:")
    # await state.update_data(waiting_for_query=message.text)
    # Проверяем текущее состояние
    # current_state = await state.get_state()
    # if current_state is not SearchState.waiting_for_query.state:
    #     await message.answer(f"search_database. current_state: {current_state}")
    #     return

    query = message.text.strip()
    # await message.answer(f"Вы ввели: {query}")

    # Здесь ваша логика поиска в БД
    urls: List[Url] = await requests.get_urls_by_text(query)
    await message.answer(f"search_database: len(urls): {len(urls)}")

    # Завершение состояния
    await state.clear()

    result = ""
    if urls:
        for url in urls:
            result += result + url.url + "\n"
        await message.answer(f"Найдено: {result}")
    else:
        await message.answer("Ничего не найдено.")


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
    # await state.clear()
    await message.answer("add_data_to_database:")
    # await state.update_data(waiting_for_input_text=message.text)
    # Проверяем текущее состояние
    current_state = await state.get_state()
    # if current_state is not SearchState.waiting_for_input_text.state:
    #     await message.answer(f"add_data_to_database. current_state: {current_state}")
    #     return
    query = message.text.strip()
    await message.answer(f"Ппробуем что-то добавить!!!")
    # Завершение состояния
    await state.clear()

