from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel


class CoverageStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    PENDING = "pending"


class EligibilityCheckBase(BaseModel):
    client_id: str
    payer: str
    check_date: datetime
    coverage_status: CoverageStatus
    effective_date: date | None = None
    termination_date: date | None = None
    plan_name: str | None = None
    failure_reason: str | None = None
    source: str = "manual"
    processed: bool = True
