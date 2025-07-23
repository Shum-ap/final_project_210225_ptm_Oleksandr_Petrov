# 🔐 Настройки подключения к MySQL
MYSQL_CONFIG = {
    "host": "ich-db.edu.itcareerhub.de",
    "user": "ich1",
    "password": "password",
    "database": "sakila",
}

# 🔐 Подключение к MongoDB (удалённый сервер)
MONGO_URI = (
    "mongodb://ich_editor:verystrongpassword"
    "@mongo.itcareerhub.de/?readPreference=primary"
    "&ssl=false&authMechanism=DEFAULT&authSource=ich_edit"
)

# 🧾 Конкретная коллекция и база для логов
MONGO_DB = "ich_edit"
MONGO_COLLECTION = "final_project_210225_ptm_Oleksandr_Petrov"
