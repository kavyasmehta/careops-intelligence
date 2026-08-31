from datetime import datetime

from app.models.user import UserBase


class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
