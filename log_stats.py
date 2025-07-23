from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

client = MongoClient(MONGO_URI)
collection = client[MONGO_DB][MONGO_COLLECTION]


def get_recent_searches(limit=5):
    """
    Возвращает 5 последних уникальных запросов (по параметрам).
    """
    seen = set()
    result = []

    for log in collection.find().sort("timestamp", -1):
        key = (log.get("search_type"), str(log.get("params")))
        if key not in seen:
            seen.add(key)
            result.append(log)
        if len(result) == limit:
            break

    return result


def get_top_searches(limit=5):
    """
    Возвращает топ N самых частых запросов по params.
    """
    pipeline = [
        {"$group": {"_id": "$params", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    return list(collection.aggregate(pipeline))
