from datetime import datetime
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Appointment(Base):
    __tablename__ = 'appointments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    photographer_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)

    photographer = relationship("User")

