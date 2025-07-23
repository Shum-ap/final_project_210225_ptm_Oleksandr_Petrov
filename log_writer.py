from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

# 🔌 Подключение к MongoDB
client = MongoClient(MONGO_URI)
collection = client[MONGO_DB][MONGO_COLLECTION]

# 🧾 Сохраняет информацию о поисковом запросе в MongoDB
def log_search(search_type, params, results_count):
    entry = {
        "timestamp": datetime.now().isoformat(),  # Время выполнения запроса
        "search_type": search_type,              # Тип запроса (keyword или genre_year)
        "params": params,                        # Введённые параметры поиска
        "results_count": results_count           # Количество результатов, найденных в MySQL
    }
    collection.insert_one(entry)  # Сохраняем в коллекцию
