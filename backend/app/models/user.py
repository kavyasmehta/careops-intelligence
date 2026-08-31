from pydantic import BaseModel

from app.core.roles import Role


class UserBase(BaseModel):
    name: str
    role: Role
    team_id: str | None = None
