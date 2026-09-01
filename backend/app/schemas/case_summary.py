from datetime import datetime

from pydantic import BaseModel


class CaseSummary(BaseModel):
    client_id: str
    summary: str
    generated_by: str  # "template" or "llm"
    disclaimer: str
    generated_at: datetime
