
# scripts/create_tables.py
from sqlmodel import SQLModel

# scripts/create_tables.py

from app.adapters.session import engine


# 👇 IMPORTANT: import models so they register
from app.db.models.appointment import Appointment  # adjust path as needed

SQLModel.metadata.create_all(bind=engine)