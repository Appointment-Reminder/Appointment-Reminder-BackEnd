import asyncio
from app.Database.client import appointments_col, photographers_col

# Sample photographers
photographers = [
    {"_id": "1", "name": "Photog A", "email": "a@example.com", "phone": "123-456-7890"},
    {"_id": "2", "name": "Photog B", "email": "b@example.com", "phone": "555-555-5555"},
]

# Sample appointments
appointments = [
    {
        "_id": "1",
        "name": "Alice",
        "surname": "Smith",
        "phone": "+123456789",
        "email": "alice@example.com",
        "time": "2025-09-10 15:00",
        "location": "Central Park",
        "photographer_id": "1",
        "balance_due": 50.0,
        "reminder_sent": False,
    },
    {
        "_id": "2",
        "name": "Bob",
        "surname": "Johnson",
        "phone": "+987654321",
        "email": "bob@example.com",
        "time": "2025-09-11 10:00",
        "location": "Studio A",
        "photographer_id": "2",
        "balance_due": 100.0,
        "reminder_sent": False,
    },
]

async def seed():
    # Clear existing data
    await appointments_col.delete_many({})
    await photographers_col.delete_many({})

    # Insert sample data
    await photographers_col.insert_many(photographers)
    await appointments_col.insert_many(appointments)
    print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
