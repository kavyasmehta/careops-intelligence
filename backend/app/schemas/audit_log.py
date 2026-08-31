from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: str
    user: str
    action: str
    entity_type: str
    entity_id: str
    timestamp: datetime
    previous_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
