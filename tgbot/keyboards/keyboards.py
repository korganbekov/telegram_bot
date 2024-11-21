import logging

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


from tgbot.database.requests import get_categories, get_priorities, get_urls_by_category, get_urls_by_priority

main = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Выберите пункт меню...", keyboard=[
    [KeyboardButton(text="Категории")],
    [KeyboardButton(text="Приоритеты")]
])

async def categories():
    # print('method categories')
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=f'{category.category}', callback_data=f'category_{category.id}'))

    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))

    # тут показывает что в одном ряду д.б. 2 клавиатуры
    return keyboard.adjust(1).as_markup()


async def priorities():
    # print('method categories')
    all_priorities = await get_priorities()
    keyboard = InlineKeyboardBuilder()
    for priority in all_priorities:
        keyboard.add(InlineKeyboardButton(text=f'{priority.priority}', callback_data=f'category_{priority.id}'))

    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))

    # тут показывает что в одном ряду д.б. 2 клавиатуры
    return keyboard.adjust(1).as_markup()

async def urls_by_category(category_id):
    # print('category_id:', category_id)
    # filter = {'category': category_id}
    logging.info(f'keyboards.urls({category_id})')
    all_items = await get_urls_by_category(category_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.url, callback_data=f'item_{item.id}'))

    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))

    # тут показывает что в одном ряду д.б. 2 клавиатуры
    return keyboard.adjust(1).as_markup()

async def urls_by_priority(priority_id):
    # print('category_id:', category_id)
    # filter = {'category': category_id}
    logging.info(f'keyboards.urls({priority_id})')
    all_items = await get_urls_by_priority(priority_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.url, callback_data=f'item_{item.id}'))

    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))

    # тут показывает что в одном ряду д.б. 2 клавиатуры
    return keyboard.adjust(1).as_markup()