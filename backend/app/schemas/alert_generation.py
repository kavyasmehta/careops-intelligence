from pydantic import BaseModel


class AlertGenerationResult(BaseModel):
    scanned_clients: int
    alerts_created: int
    alerts_skipped_as_duplicate: int
    created_by_type: dict[str, int]
