from datetime import datetime

from pydantic import BaseModel

from app.models.client import Address, ClientBase, ClientStatus


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: Address | None = None
    assigned_team_id: str | None = None
    assigned_employee_id: str | None = None
    status: ClientStatus | None = None


class ClientRead(ClientBase):
    id: str
    created_at: datetime
    updated_at: datetime
