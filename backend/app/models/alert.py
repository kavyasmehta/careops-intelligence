from enum import StrEnum

from pydantic import BaseModel


class AlertType(StrEnum):
    APPOINTMENT_WITHOUT_AUTHORIZATION = "appointment_without_authorization"
    AUTHORIZATION_EXPIRING = "authorization_expiring"
    AUTHORIZATION_UNITS_EXHAUSTED = "authorization_units_exhausted"
    ELIGIBILITY_FAILED = "eligibility_failed"
    COVERAGE_ENDING_SOON = "coverage_ending_soon"
    OVERDUE_TASK = "overdue_task"
    MULTIPLE_UNRESOLVED_ISSUES = "multiple_unresolved_issues"


class AlertSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class AlertBase(BaseModel):
    client_id: str
    alert_type: AlertType
    severity: AlertSeverity
    explanation: str
    recommended_action: str
    assigned_employee_id: str | None = None
    status: AlertStatus = AlertStatus.OPEN
