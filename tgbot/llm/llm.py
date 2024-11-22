from transformers import pipeline

# Загрузка предобученной модели для классификации
classifier = pipeline("text-classification", model="distilbert-base-uncased", return_all_scores=True)

# Категории для классификации
CATEGORIES = {
    "Социальные сети": ["facebook", "instagram", "vk", "telegram", "twitter", "tiktok", "vk"],
    "Видео": ["youtube", "vimeo", "twitch"],
    "Новостные сайты": ["bbc", "cnn", "reuters"],
    "Интернет-магазины": ["amazon", "ebay", "wildberries", "ozon", "alibaba"],
    "Почта": ["mail", "hotmail", "gmail"],
    "Файловые хранилища": ["drive.google.com", "dropbox.com", "yadi.sk"],
}

PRIORITIES = {
    "Высокий": ["urgent", "important", "critical"],
    "Средний": ["normal", "regular"],
    "Низкий": ["low", "optional"],
}

async def predict_category_and_priority(text):
    try:
        # Предсказание категории
        category_scores = classifier(text)
        category = max(CATEGORIES.keys(), key=lambda cat: sum(
            [score['score'] for score in category_scores[0] if any(keyword in score['label'] for keyword in CATEGORIES[cat])]))

        # Предсказание приоритета
        priority_scores = classifier(text)
        priority = max(PRIORITIES.keys(), key=lambda prio: sum(
            [score['score'] for score in priority_scores[0] if any(keyword in score['label'] for keyword in PRIORITIES[prio])]))

        return category, priority
    except Exception:
        return "Неизвестная категория", "Неизвестный приоритет"
