# 🔍 Проверка подключения к MySQL и MongoDB

from pymongo import MongoClient
from pymysql import connect, OperationalError
from config import MYSQL_CONFIG, MONGO_URI, MONGO_DB, MONGO_COLLECTION

def test_mysql_connection():
    print("🔌 Проверка подключения к MySQL...")
    try:
        conn = connect(**MYSQL_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM film")
            count = cursor.fetchone()[0]
            print(f"✅ Успешно! Количество фильмов в базе: {count}")
        conn.close()
    except OperationalError as e:
        print(f"❌ Ошибка подключения к MySQL: {e}")

def test_mongo_connection():
    print("\n🔌 Проверка подключения к MongoDB...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        db = client[MONGO_DB]
        print("✅ Успешно! Коллекции в базе:")
        for name in db.list_collection_names():
            prefix = "➡️ " if name == MONGO_COLLECTION else "   "
            print(f"{prefix}{name}")
    except Exception as e:
        print(f"❌ Ошибка подключения к MongoDB: {e}")

# ▶️ Запуск при вызове файла
if __name__ == "__main__":
    test_mysql_connection()
    test_mongo_connection()
