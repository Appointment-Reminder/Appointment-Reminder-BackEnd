from app.routes.appointments import Appointment
from app.models.reminder import ReminderRequest, Reminder
from app.models.photographer import Photographer

DUMMY_APPOINTMENTS = [
    Appointment(id="1", name="Alice", surname="Smith", phone="+123456789",
                email="alice@example.com", time="2025-09-10 15:00", location="Central Park"),
    Appointment(id="2", name="Bob", surname="Johnson", phone="+987654321",
                email="bob@example.com", time="2025-09-11 10:00", location="Studio A"),
]


DUMMY_REMINDERS = [
    Reminder(id= "r1", appointment_id= "1", template= "Hello {Client}", status= "pending"),
]

DUMMY_PHOTOGRAPHERS = [
    Photographer(id="1", name="Eve", email="eve@example.com"),
    Photographer(id="2", name="Mallory", email="mallory@example.com"),
]

class MockPhotographersCollection:
    def __init__(self):
        self.data = DUMMY_PHOTOGRAPHERS.copy()

    def find(self):
        class Cursor:
            async def to_list(_, length):
                return self.data
        return Cursor()

    async def find_one(self, query):
        for r in self.data:
            if r.id == query["_id"]:
                return r
        return None
    async def insert_one(self, doc):
        self.data.append(doc)

    async def replace_one(self, query, doc):
        for i, r in enumerate(self.data):
            if r.id == query["_id"]:
                self.data[i] = doc
                return type("obj", (), {"matched_count": 1})
        return type("obj", (), {"matched_count": 0})

    async def delete_one(self, query):
        before = len(self.data)
        self.data = [r for r in self.data if r.id != query["_id"]]
        deleted = before - len(self.data)
        return type("obj", (), {"deleted_count": deleted})

class MockAppointmentsCollection:
    def __init__(self):
        self.data = DUMMY_APPOINTMENTS.copy()

    def find(self):
        class Cursor:
            async def to_list(_, length):
                return self.data
        return Cursor()

    async def find_one(self, query):
        for r in self.data:
            if r.id == query["_id"]:
                return r
        return None
    async def insert_one(self, doc):
        self.data.append(doc)

    async def replace_one(self, query, doc):
        for i, r in enumerate(self.data):
            if r.id == query["_id"]:
                self.data[i] = doc
                return type("obj", (), {"matched_count": 1})
        return type("obj", (), {"matched_count": 0})

    async def delete_one(self, query):
        before = len(self.data)
        self.data = [r for r in self.data if r.id != query["_id"]]
        deleted = before - len(self.data)
        return type("obj", (), {"deleted_count": deleted})


class MockRemindersCollection:
    def __init__(self):
        self.data = DUMMY_REMINDERS.copy()

    def find(self):
        class Cursor:
            async def to_list(_, length):
                return self.data
        return Cursor()

    async def find_one(self, query):
        for r in self.data:
            if r.id == query["_id"]:
                return r
        return None
    async def insert_one(self, doc):
        self.data.append(doc)

    async def replace_one(self, query, doc):
        for i, r in enumerate(self.data):
            if r.id == query["_id"]:
                self.data[i] = doc
                return type("obj", (), {"matched_count": 1})
        return type("obj", (), {"matched_count": 0})

    async def delete_one(self, query):
        before = len(self.data)
        self.data = [r for r in self.data if r.id != query["_id"]]
        deleted = before - len(self.data)
        return type("obj", (), {"deleted_count": deleted})

