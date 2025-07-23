# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем .env один раз

# MongoDB
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# Сформированный URI
MONGO_URI = (
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}/"
    f"?readPreference=primary&ssl=false&authMechanism=DEFAULT&authSource={MONGO_DB}"
)
