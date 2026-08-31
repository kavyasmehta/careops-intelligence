from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class AppointmentStatus(StrEnum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentBase(BaseModel):
    client_id: str
    appointment_datetime: datetime
    service_type: str
    provider: str
    location: str
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    authorization_id: str | None = None
