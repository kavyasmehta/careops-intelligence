from datetime import datetime

from pydantic import BaseModel

from app.models.appointment import AppointmentBase, AppointmentStatus


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    status: AppointmentStatus | None = None
    authorization_id: str | None = None
    provider: str | None = None
    location: str | None = None


class AppointmentRead(AppointmentBase):
    id: str
    created_at: datetime
    updated_at: datetime
