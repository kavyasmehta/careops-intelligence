from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.authorization import AuthorizationBase, AuthorizationStatus


class AuthorizationCreate(AuthorizationBase):
    pass


class AuthorizationUpdate(BaseModel):
    units_used: int | None = Field(default=None, ge=0)
    status: AuthorizationStatus | None = None
    expiration_date: date | None = None


class AuthorizationRead(AuthorizationBase):
    id: str
    created_at: datetime
    updated_at: datetime
