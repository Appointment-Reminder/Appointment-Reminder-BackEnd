from enum import Enum


class AppointmentStatus(str, Enum):
    PENDING = "pending"
    NEEDS_ASSIGNMENT = "needs_assignment"
    CONFIRMED = "confirmed"
    # ...whatever else already exists implicitly as string literals