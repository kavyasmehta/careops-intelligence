from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class AuthorizationStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    EXHAUSTED = "exhausted"
    DENIED = "denied"


class AuthorizationBase(BaseModel):
    client_id: str
    payer: str
    authorization_number: str
    service_type: str
    units_approved: int = Field(gt=0)
    units_used: int = Field(default=0, ge=0)
    effective_date: date
    expiration_date: date
    status: AuthorizationStatus = AuthorizationStatus.PENDING

    @model_validator(mode="after")
    def check_dates_and_units(self) -> "AuthorizationBase":
        if self.expiration_date <= self.effective_date:
            raise ValueError("expiration_date must be after effective_date")
        if self.units_used > self.units_approved:
            raise ValueError("units_used cannot exceed units_approved")
        return self
