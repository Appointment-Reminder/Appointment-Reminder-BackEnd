import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "PhotoReminder_dev")  # change per env

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

appointments_col = db["appointments"]
photographers_col = db["photographers"]
reminders_col = db["reminders"]

