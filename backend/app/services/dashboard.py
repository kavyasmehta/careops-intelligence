"""Executive dashboard aggregation.

Computed with plain Python over `find()` results rather than Mongo
aggregation pipelines — the dataset (hundreds, not millions, of
documents) makes this simpler to read and just as fast, and it keeps
the filter semantics (team -> client scope -> everything else) in one
place instead of spread across several pipeline stages.

Filter semantics: `team_id` scopes the client population (and, through
it, every client-linked record); `payer` scopes payer-bearing records
directly; `status` overrides which client status the "active clients"
KPI counts (defaults to "active"); `date_from`/`date_to` bound the
trend charts and the two averaged/rate metrics.
"""
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.dashboard import (
    DashboardMetrics,
    EmployeeWorkload,
    PayerPerformance,
    StatusCount,
    TrendPoint,
)

HIGH_PRIORITY_SEVERITIES = ["high", "critical"]
EXPIRING_WINDOW_DAYS = 14
DEFAULT_TREND_DAYS = 30
EXPIRATION_TREND_WEEKS = 8


def _parse_dt(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    return None


async def compute_metrics(
    db: AsyncIOMotorDatabase,
    *,
    team_id: str | None,
    payer: str | None,
    status: str | None,
    date_from: date | None,
    date_to: date | None,
) -> DashboardMetrics:
    today = date.today()
    range_from = date_from or (today - timedelta(days=DEFAULT_TREND_DAYS))
    range_to = date_to or today

    client_scope_filter: dict = {}
    if team_id:
        client_scope_filter["assigned_team_id"] = team_id
    clients = await db["clients"].find(client_scope_filter).to_list(length=None)
    client_ids = {str(c["_id"]) for c in clients} if team_id else None  # None = no client-id scoping needed

    active_status = status or "active"
    if team_id:
        active_clients = sum(1 for c in clients if c["status"] == active_status)
    else:
        active_clients = await db["clients"].count_documents({"status": active_status})

    def scoped(base: dict, client_id_field: str = "client_id") -> dict:
        result = dict(base)
        if client_ids is not None:
            result[client_id_field] = {"$in": list(client_ids)}
        return result

    # --- Eligibility ---
    eligibility_filter = scoped({})
    if payer:
        eligibility_filter["payer"] = payer
    eligibility_checks = await db["eligibility_checks"].find(eligibility_filter).to_list(length=None)
    total_checks = len(eligibility_checks)
    success_checks = sum(1 for c in eligibility_checks if c["coverage_status"] == "active")
    eligibility_success_rate = round(100 * success_checks / total_checks, 1) if total_checks else 0.0

    # --- Upcoming appointments ---
    now_iso = datetime.now(UTC).isoformat()
    appt_filter = scoped({"status": "scheduled", "appointment_datetime": {"$gt": now_iso}})
    upcoming_appointments = await db["appointments"].count_documents(appt_filter)

    # --- Expiring authorizations ---
    auth_filter = scoped(
        {
            "status": {"$in": ["active", "pending"]},
            "expiration_date": {
                "$gte": today.isoformat(),
                "$lte": (today + timedelta(days=EXPIRING_WINDOW_DAYS)).isoformat(),
            },
        }
    )
    if payer:
        auth_filter["payer"] = payer
    expiring_authorizations = await db["authorizations"].count_documents(auth_filter)

    # --- Alerts ---
    alert_filter = scoped({"status": {"$ne": "resolved"}, "severity": {"$in": HIGH_PRIORITY_SEVERITIES}})
    open_high_priority_alerts = await db["alerts"].count_documents(alert_filter)

    resolved_filter = scoped({"status": "resolved"})
    resolved_alerts = await db["alerts"].find(resolved_filter).to_list(length=None)
    resolution_hours = []
    for alert in resolved_alerts:
        created = _parse_dt(alert.get("created_at"))
        resolved = _parse_dt(alert.get("resolved_at"))
        if created and resolved:
            resolution_hours.append((resolved - created).total_seconds() / 3600)
    avg_resolution_time_hours = round(sum(resolution_hours) / len(resolution_hours), 1) if resolution_hours else None

    # --- Cases by status ---
    status_counts: dict[str, int] = defaultdict(int)
    for c in clients:
        status_counts[c["status"]] += 1
    cases_by_status = [StatusCount(label=k, count=v) for k, v in sorted(status_counts.items())]

    # --- Eligibility trend (daily check volume, range_from..range_to) ---
    trend_counts: dict[str, int] = defaultdict(int)
    for check in eligibility_checks:
        check_dt = _parse_dt(check.get("check_date"))
        if check_dt and range_from <= check_dt.date() <= range_to:
            trend_counts[check_dt.date().isoformat()] += 1
    eligibility_trend = [
        TrendPoint(label=d.isoformat(), value=trend_counts.get(d.isoformat(), 0))
        for d in _date_range(range_from, range_to)
    ]

    # --- Authorization expiration trend (next N weeks) ---
    all_auths = await db["authorizations"].find(scoped({"status": {"$in": ["active", "pending"]}})).to_list(
        length=None
    )
    if payer:
        all_auths = [a for a in all_auths if a["payer"] == payer]
    week_counts: dict[int, int] = defaultdict(int)
    for auth in all_auths:
        exp = date.fromisoformat(auth["expiration_date"])
        delta_weeks = (exp - today).days // 7
        if 0 <= delta_weeks < EXPIRATION_TREND_WEEKS:
            week_counts[delta_weeks] += 1
    authorization_expiration_trend = [
        TrendPoint(label=f"Week {i + 1}", value=week_counts.get(i, 0)) for i in range(EXPIRATION_TREND_WEEKS)
    ]

    # --- Workload by employee (open tasks + open alerts) ---
    employee_filter = {"team_id": team_id} if team_id else {}
    employees = await db["users"].find(employee_filter).to_list(length=None)
    workload_by_employee = []
    for emp in employees:
        emp_id = str(emp["_id"])
        open_tasks = await db["tasks"].count_documents({"assigned_employee_id": emp_id, "status": {"$ne": "completed"}})
        open_alerts = await db["alerts"].count_documents({"assigned_employee_id": emp_id, "status": {"$ne": "resolved"}})
        workload_by_employee.append(
            EmployeeWorkload(employee_id=emp_id, employee_name=emp["name"], open_items=open_tasks + open_alerts)
        )
    workload_by_employee.sort(key=lambda w: w.open_items, reverse=True)

    # --- Payer performance ---
    payer_groups: dict[str, list[dict]] = defaultdict(list)
    for check in eligibility_checks:
        payer_groups[check["payer"]].append(check)
    payer_performance = []
    for payer_name, checks in sorted(payer_groups.items()):
        successes = sum(1 for c in checks if c["coverage_status"] == "active")
        payer_performance.append(
            PayerPerformance(
                payer=payer_name,
                total_checks=len(checks),
                success_rate=round(100 * successes / len(checks), 1) if checks else 0.0,
            )
        )

    return DashboardMetrics(
        active_clients=active_clients,
        eligibility_success_rate=eligibility_success_rate,
        upcoming_appointments=upcoming_appointments,
        expiring_authorizations=expiring_authorizations,
        open_high_priority_alerts=open_high_priority_alerts,
        avg_resolution_time_hours=avg_resolution_time_hours,
        cases_by_status=cases_by_status,
        eligibility_trend=eligibility_trend,
        authorization_expiration_trend=authorization_expiration_trend,
        workload_by_employee=workload_by_employee,
        payer_performance=payer_performance,
    )


def _date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)
