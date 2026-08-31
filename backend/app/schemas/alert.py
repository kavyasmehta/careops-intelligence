from datetime import datetime

from pydantic import BaseModel

from app.models.alert import AlertBase, AlertSeverity, AlertStatus


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    assigned_employee_id: str | None = None
    status: AlertStatus | None = None
    resolution_notes: str | None = None


class AlertRead(AlertBase):
    id: str
    resolution_notes: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
