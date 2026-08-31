from datetime import datetime

from pydantic import BaseModel

from app.models.eligibility import CoverageStatus, EligibilityCheckBase


class EligibilityCheckCreate(EligibilityCheckBase):
    pass


class EligibilityCheckUpdate(BaseModel):
    coverage_status: CoverageStatus | None = None
    failure_reason: str | None = None
    processed: bool | None = None


class EligibilityCheckRead(EligibilityCheckBase):
    id: str
    created_at: datetime
    updated_at: datetime
