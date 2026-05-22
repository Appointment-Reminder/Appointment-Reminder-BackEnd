
# scripts/create_tables.py
from app.db.session import engine
from sqlmodel import SQLModel

# scripts/create_tables.py

from app.db.session import engine


# 👇 IMPORTANT: import models so they register
from app.db.models.appointment import Appointment  # adjust path as needed

SQLModel.metadata.create_all(bind=engine)