"""Analytics computations that complement (not duplicate) the dashboard:
resolution-time breakdown, outcome distributions, team-level workload, and
a longer-range operational trend. Same "plain Python over find()" approach
as the dashboard service — the dataset size doesn't need aggregation
pipelines to stay fast, and this stays far easier to read/test.
"""
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.analytics import (
    AnalyticsOverview,
    FailureReasonCount,
    OutcomeCount,
    ResolutionTimeBySeverity,
    TeamWorkload,
    WeeklyTrendPoint,
)

TREND_WEEKS = 12


def _parse_dt(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    return None


def _outcome_counts(items: list[dict], field: str) -> list[OutcomeCount]:
    counts: dict[str, int] = defaultdict(int)
    for item in items:
        counts[item[field]] += 1
    total = len(items)
    return [
        OutcomeCount(label=label, count=count, pct=round(100 * count / total, 1) if total else 0.0)
        for label, count in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    ]


async def compute_overview(db: AsyncIOMotorDatabase) -> AnalyticsOverview:
    alerts = await db["alerts"].find({}).to_list(length=None)
    authorizations = await db["authorizations"].find({}).to_list(length=None)
    eligibility_checks = await db["eligibility_checks"].find({}).to_list(length=None)
    users = await db["users"].find({}).to_list(length=None)
    clients = await db["clients"].find({}).to_list(length=None)
    tasks = await db["tasks"].find({}).to_list(length=None)

    # Resolution time by severity
    hours_by_severity: dict[str, list[float]] = defaultdict(list)
    for alert in alerts:
        if alert["status"] != "resolved":
            continue
        created = _parse_dt(alert.get("created_at"))
        resolved = _parse_dt(alert.get("resolved_at"))
        if created and resolved:
            hours_by_severity[alert["severity"]].append((resolved - created).total_seconds() / 3600)
    resolution_time_by_severity = [
        ResolutionTimeBySeverity(severity=sev, avg_hours=round(sum(hrs) / len(hrs), 1), resolved_count=len(hrs))
        for sev, hrs in sorted(hours_by_severity.items())
    ]

    authorization_outcomes = _outcome_counts(authorizations, "status")
    eligibility_outcomes = _outcome_counts(eligibility_checks, "coverage_status")

    reason_counts: dict[str, int] = defaultdict(int)
    for check in eligibility_checks:
        if check.get("failure_reason"):
            reason_counts[check["failure_reason"]] += 1
    top_failure_reasons = [
        FailureReasonCount(reason=reason, count=count)
        for reason, count in sorted(reason_counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    ]

    # Team workload: roll employee-level open alerts/tasks up to their team
    employee_team = {str(u["_id"]): u.get("team_id") for u in users}
    client_team_counts: dict[str, int] = defaultdict(int)
    for c in clients:
        if c.get("assigned_team_id"):
            client_team_counts[c["assigned_team_id"]] += 1

    open_alerts_by_team: dict[str, int] = defaultdict(int)
    for alert in alerts:
        if alert["status"] == "resolved":
            continue
        team = employee_team.get(alert.get("assigned_employee_id"))
        if team:
            open_alerts_by_team[team] += 1

    open_tasks_by_team: dict[str, int] = defaultdict(int)
    for task in tasks:
        if task["status"] == "completed":
            continue
        team = employee_team.get(task.get("assigned_employee_id"))
        if team:
            open_tasks_by_team[team] += 1

    all_teams = set(client_team_counts) | set(open_alerts_by_team) | set(open_tasks_by_team)
    team_workload = [
        TeamWorkload(
            team=team,
            client_count=client_team_counts.get(team, 0),
            open_alerts=open_alerts_by_team.get(team, 0),
            open_tasks=open_tasks_by_team.get(team, 0),
        )
        for team in sorted(all_teams)
    ]

    # Alerts-created trend, last TREND_WEEKS weeks
    today = datetime.now(UTC).date()
    week_counts: dict[int, int] = defaultdict(int)
    for alert in alerts:
        created = _parse_dt(alert.get("created_at"))
        if not created:
            continue
        weeks_ago = (today - created.date()).days // 7
        if 0 <= weeks_ago < TREND_WEEKS:
            week_counts[weeks_ago] += 1
    alerts_created_trend = [
        WeeklyTrendPoint(week_label=f"{i}w ago" if i else "This week", alerts_created=week_counts.get(i, 0))
        for i in range(TREND_WEEKS - 1, -1, -1)
    ]

    return AnalyticsOverview(
        resolution_time_by_severity=resolution_time_by_severity,
        authorization_outcomes=authorization_outcomes,
        eligibility_outcomes=eligibility_outcomes,
        top_failure_reasons=top_failure_reasons,
        team_workload=team_workload,
        alerts_created_trend=alerts_created_trend,
    )
