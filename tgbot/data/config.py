import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv('BOT_TOKEN')

DATABASE_URL: str = os.getenv('DATABASE_URL')

NOTION_TOKEN=os.getenv('NOTION_TOKEN')

CATEGORIES = [
    "Социальные сети", "Видео", "Новостные сайты", "Интернет-магазины", "Почта", "Файловые хранилища", "Неизвестная категория"
]

PRIORITIES = ["Высокий", "Средний", "Низкий", "Неизвестный приоритет"]


# Категории для классификации
CATEGORIES_LLM = {
    "Социальные сети": ["facebook", "instagram", "vk", "telegram", "twitter", "tiktok", "vk"],
    "Видео": ["youtube", "vimeo", "twitch"],
    "Новостные сайты": ["bbc", "cnn", "reuters"],
    "Интернет-магазины": ["amazon", "ebay", "wildberries", "ozon", "alibaba"],
    "Почта": ["mail", "hotmail", "gmail"],
    "Файловые хранилища": ["drive.google.com", "dropbox.com", "yadi.sk"],
}

PRIORITIES_LLM = {
    "Высокий": ["urgent", "important", "critical"],
    "Средний": ["normal", "regular"],
    "Низкий": ["low", "optional"],
}

# Словарь категорий и соответствующих паттернов
CATEGORIES_COMMANDS = {
    "Социальные сети": [r"instagram\.com", r"facebook\.com", r"twitter\.com", r"tiktok\.com", r"vk\.*"],
    "Видео": [r"youtube\.com", r"vimeo\.com", r"twitch\.tv"],
    "Новостные сайты": [r"bbc\.com", r"cnn\.com"],
    "Интернет-магазины": [r"amazon\.com", r"ebay\.com", r"wildberries\.ru"],
    "Образование": [r"coursera\.org", r"wikipedia\.org", r"udemy\.com"],
    "Файловые хранилища": [r"drive\.google\.com", r"dropbox\.com", r"yadi\.sk"],
    "Почта": [r"gmail\.com", r"mail\.ru", r"hotmail\.*"],
}