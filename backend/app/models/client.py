from datetime import date
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class ClientStatus(StrEnum):
    ACTIVE = "active"
    PENDING = "pending"
    INACTIVE = "inactive"
    DISCHARGED = "discharged"


class Address(BaseModel):
    line1: str
    city: str
    state: str
    zip_code: str = Field(alias="zip")

    model_config = {"populate_by_name": True}


class ClientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    member_id: str = Field(description="Medicaid or member ID")
    email: EmailStr | None = None
    phone: str | None = None
    address: Address | None = None
    assigned_team_id: str | None = None
    assigned_employee_id: str | None = None
    status: ClientStatus = ClientStatus.PENDING
