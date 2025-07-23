from pymongo import MongoClient

client = MongoClient("mongodb://ich_editor:verystrongpassword@mongo.itcareerhub.de/?readPreference=primary&ssl=false&authMechanism=DEFAULT&authSource=ich_edit")
db = client["ich_edit"]
collection = db["final_project_210225_ptm_Oleksandr_Petrov"]

for log in collection.find().limit(5):
    print(log)
