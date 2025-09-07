import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "PhotoReminder_Test"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

async def seed():
    # Clear old data
    await db["appointments"].delete_many({})
    await db["photographers"].delete_many({})
    await db["reminders"].delete_many({})

    # Insert dummy photographers
    await db["photographers"].insert_many([
        {"_id": "p1", "name": "Alice", "specialty": "Portrait"},
        {"_id": "p2", "name": "Bob", "specialty": "Landscape"},
    ])

    # Insert dummy appointments
    await db["appointments"].insert_many([
        {"_id": "a1", "client": "Charlie", "time": "2025-09-10 10:00", "location": "Studio A", "photographer_id": "p1"},
        {"_id": "a2", "client": "Dana", "time": "2025-09-11 14:00", "location": "Studio B", "photographer_id": "p2"},
    ])

    # Insert dummy reminders
    await db["reminders"].insert_many([
        {"_id": "r1", "appointment_id": "a1", "message": "Reminder for Charlie"},
        {"_id": "r2", "appointment_id": "a2", "message": "Reminder for Dana"},
    ])

    print("✅ Test DB seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
