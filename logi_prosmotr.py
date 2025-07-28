from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

mongo_user = os.getenv("MONGO_USER")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_host = os.getenv("MONGO_HOST")
mongo_db = os.getenv("MONGO_DB", "ich_edit")
mongo_collection = os.getenv("MONGO_COLLECTION", "final_project_210225_ptm_Oleksandr_Petrov")

if not all([mongo_user, mongo_password, mongo_host]):
    raise ValueError("Не заданы необходимые переменные для подключения к MongoDB")

mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}/?readPreference=primary&ssl=false&authMechanism=DEFAULT&authSource={mongo_db}"

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]

for log in collection.find().limit(5):
    print(log)
