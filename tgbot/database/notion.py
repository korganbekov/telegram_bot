from notion_client import Client
from tgbot.data import config
import asyncio

# Создаем клиент Notion
notion = Client(auth=config.NOTION_TOKEN)

# ID базы данных
DATABASE_ID = "your_database_id"

async def save_to_notion(data):
    """
    Сохраняет данные в базу данных Notion.
    :param data: Словарь с данными для сохранения.
    """
    try:
        # Формируем запрос для добавления данных
        response = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Title": {
                    "title": [
                        {"text": {"content": data["title"]}}
                    ]
                },
                "URL": {
                    "url": data["url"]
                },
                "Category": {
                    "select": {"name": data["category"]}
                },
                "Priority": {
                    "number": data["priority"]
                },
                "Timestamp": {
                    "date": {"start": data["timestamp"]}
                }
            }
        )
        print(f"Page created successfully: {response['id']}")
    except Exception as e:
        print(f"Error while saving to Notion: {e}")


# Пример вызова
data = {
    "title": "Gmail",
    "url": "https://gmail.com",
    "category": "Email",
    "priority": 2,
    "timestamp": "2024-11-21T10:00:00.000Z"
}

# await save_to_notion(data)
