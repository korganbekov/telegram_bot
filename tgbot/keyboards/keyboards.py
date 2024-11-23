import logging

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.database.requests import get_categories, get_priorities, get_urls_by_category, get_urls_by_priority

main = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...", keyboard=[
    [KeyboardButton(text="Категории")],
    [KeyboardButton(text="Приоритеты")],
    [KeyboardButton(text="Поиск ссылки по тексту")]
])


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=f'{category.category}', callback_data=f'category_{category.id}'))

    return keyboard.adjust(1).as_markup()


async def priorities():
    all_priorities = await get_priorities()
    keyboard = InlineKeyboardBuilder()
    for priority in all_priorities:
        keyboard.add(InlineKeyboardButton(text=f'{priority.priority}', callback_data=f'category_{priority.id}'))

    return keyboard.adjust(1).as_markup()


async def urls_by_category(category_id):
    all_items = await get_urls_by_category(category_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.url, callback_data=f'item_{item.id}'))

    return keyboard.adjust(1).as_markup()


async def urls_by_priority(priority_id):
    all_items = await get_urls_by_priority(priority_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.url, callback_data=f'item_{item.id}'))

    return keyboard.adjust(1).as_markup()


async def urls_to_save(urls):
    logging.warning(f'urls_to_save. urls: {urls}')
    keyboard = InlineKeyboardBuilder()
    for idx, url in enumerate(urls):
        logging.warning(f'urls_to_save. url: {url}')
        keyboard.add(InlineKeyboardButton(text=f"Сохранить: {url}", callback_data=f"save_url_{idx}"))

    # Добавить кнопку для отмены сохранения
    # keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="cancel_save"))

    return keyboard.adjust(1).as_markup()
