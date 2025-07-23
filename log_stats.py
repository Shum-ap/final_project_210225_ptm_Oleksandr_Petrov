from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

client = MongoClient(MONGO_URI)
collection = client[MONGO_DB][MONGO_COLLECTION]

# 🕒 Получает 5 последних УНИКАЛЬНЫХ запросов из логов MongoDB
def get_recent_searches(limit=5):
    seen = set()
    result = []

    for log in collection.find().sort("timestamp", -1):  # сортировка по убыванию времени
        key = (log.get("search_type"), str(log.get("params")))  # ключ уникальности
        if key not in seen:
            seen.add(key)
            result.append(log)
        if len(result) == limit:
            break

    return result

# 📊 Возвращает топ-N наиболее частых запросов (по параметрам)
def get_top_searches(limit=5):
    pipeline = [
        {"$group": {"_id": "$params", "count": {"$sum": 1}}},  # группировка по params
        {"$sort": {"count": -1}},                              # сортировка по убыванию
        {"$limit": limit}                                      # ограничение по количеству
    ]
    return list(collection.aggregate(pipeline))  # агрегируем и возвращаем список
