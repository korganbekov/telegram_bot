from transformers import pipeline

from tgbot.data.config import CATEGORIES_LLM as CATEGORIES, PRIORITIES_LLM as PRIORITIES

# Загрузка предобученной модели для классификации
classifier = pipeline("text-classification", model="distilbert-base-uncased", return_all_scores=True)



async def predict_category_and_priority(text):
    try:
        # Предсказание категории
        category_scores = classifier(text)
        category = max(CATEGORIES.keys(), key=lambda cat: sum(
            [score['score'] for score in category_scores[0] if any(keyword in score['label'] for keyword in CATEGORIES_LLM[cat])]))

        # Предсказание приоритета
        priority_scores = classifier(text)
        priority = max(PRIORITIES.keys(), key=lambda prio: sum(
            [score['score'] for score in priority_scores[0] if any(keyword in score['label'] for keyword in PRIORITIES_LLM[prio])]))

        return category, priority
    except Exception:
        return "Неизвестная категория", "Неизвестный приоритет"
