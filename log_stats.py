from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from pymongo import MongoClient

client = MongoClient(MONGO_URI)
collection = client[MONGO_DB][MONGO_COLLECTION]

def get_recent_searches(limit=5):
    return list(collection.find().sort("timestamp", -1).limit(limit))

def get_top_searches(limit=5):
    pipeline = [
        {"$group": {"_id": "$params", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    return list(collection.aggregate(pipeline))
