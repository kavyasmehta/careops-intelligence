from pydantic import BaseModel


class StatusCount(BaseModel):
    label: str
    count: int


class TrendPoint(BaseModel):
    label: str
    value: int


class EmployeeWorkload(BaseModel):
    employee_id: str
    employee_name: str
    open_items: int


class PayerPerformance(BaseModel):
    payer: str
    total_checks: int
    success_rate: float


class DashboardMetrics(BaseModel):
    active_clients: int
    eligibility_success_rate: float
    upcoming_appointments: int
    expiring_authorizations: int
    open_high_priority_alerts: int
    avg_resolution_time_hours: float | None
    cases_by_status: list[StatusCount]
    eligibility_trend: list[TrendPoint]
    authorization_expiration_trend: list[TrendPoint]
    workload_by_employee: list[EmployeeWorkload]
    payer_performance: list[PayerPerformance]
