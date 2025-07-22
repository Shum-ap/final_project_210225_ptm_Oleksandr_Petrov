from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

client = MongoClient(MONGO_URI)
collection = client[MONGO_DB][MONGO_COLLECTION]

def log_search(search_type, params, results_count):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "search_type": search_type,
        "params": params,
        "results_count": results_count
    }
    collection.insert_one(entry)
