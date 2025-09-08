from app.routes.appointments import Appointment
from app.models.reminder import ReminderRequest
from app.models.photographer import Photographer

DUMMY_APPOINTMENTS = [
    Appointment(id="1", name="Alice", surname="Smith", phone="+123456789",
                email="alice@example.com", time="2025-09-10 15:00", location="Central Park"),
    Appointment(id="2", name="Bob", surname="Johnson", phone="+987654321",
                email="bob@example.com", time="2025-09-11 10:00", location="Studio A"),
]



DUMMY_PHOTOGRAPHERS = [
    Photographer(id="1", name="Eve", email="eve@example.com"),
    Photographer(id="2", name="Mallory", email="mallory@example.com"),
]

class MockPhotographersCollection:
    def find(self):
        class Cursor:
            async def to_list(self, length):
                return [p.dict() for p in DUMMY_PHOTOGRAPHERS]
        return Cursor()

    async def find_one(self, query):
        for p in DUMMY_PHOTOGRAPHERS:
            if p.id == query["_id"]:
                return p.dict()
        return None

class MockAppointmentsCollection:
    def find(self):
        class Cursor:
            async def to_list(self, length):
                return [appt.dict() for appt in DUMMY_APPOINTMENTS]
        return Cursor()

    async def find_one(self, query):
        for appt in DUMMY_APPOINTMENTS:
            if appt.id == query["_id"]:
                return appt.dict()
        return None

