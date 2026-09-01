from pydantic import BaseModel


class ResolutionTimeBySeverity(BaseModel):
    severity: str
    avg_hours: float
    resolved_count: int


class OutcomeCount(BaseModel):
    label: str
    count: int
    pct: float


class FailureReasonCount(BaseModel):
    reason: str
    count: int


class TeamWorkload(BaseModel):
    team: str
    client_count: int
    open_alerts: int
    open_tasks: int


class WeeklyTrendPoint(BaseModel):
    week_label: str
    alerts_created: int


class AnalyticsOverview(BaseModel):
    resolution_time_by_severity: list[ResolutionTimeBySeverity]
    authorization_outcomes: list[OutcomeCount]
    eligibility_outcomes: list[OutcomeCount]
    top_failure_reasons: list[FailureReasonCount]
    team_workload: list[TeamWorkload]
    alerts_created_trend: list[WeeklyTrendPoint]
