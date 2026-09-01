"""Automatic alert generation.

Scans current operational data for the 7 conditions the spec calls for
and creates an Alert for each one that doesn't already have an active
(non-resolved) alert of the same type for that client — the same
dedup rule enforced by AlertService.create, applied here in bulk so
this can run as a one-off admin-triggered sweep (POST
/api/v1/alerts/generate) standing in for what would be a scheduled job
in a real deployment.

Bulk-fetches each collection once and groups in Python rather than
per-client queries — same approach as the dashboard/analytics
services, and fast enough at this dataset size. The severity/
explanation phrasing intentionally matches scripts/seed_mongo.py's
alert generation so freshly-generated alerts read consistently with
seeded ones; the two aren't shared code because one runs once against
a fixed synthetic snapshot and the other runs live against whatever
the database currently contains.
"""
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.alert import AlertSeverity, AlertStatus
from app.repositories.alerts import AlertRepository
from app.schemas.alert_generation import AlertGenerationResult
from app.services.audit import record_audit

GENERATED_BY_USER = "system (automatic alert generation)"

EXPIRING_WINDOW_DAYS = 14
COVERAGE_ENDING_WINDOW_DAYS = 30
UNITS_EXHAUSTED_THRESHOLD = 0.9
MULTIPLE_ISSUES_THRESHOLD = 3


def _parse_date(value) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value) if isinstance(value, str) else value


async def _candidates(db: AsyncIOMotorDatabase) -> dict[str, list[dict]]:
    today = date.today()
    now_iso = datetime.now(UTC).isoformat()

    eligibility_checks = await db["eligibility_checks"].find({}).sort("check_date", -1).to_list(length=None)
    authorizations = await db["authorizations"].find({}).to_list(length=None)
    appointments = await db["appointments"].find({}).to_list(length=None)
    tasks = await db["tasks"].find({}).to_list(length=None)

    pools: dict[str, list[dict]] = defaultdict(list)

    latest_by_client: dict[str, dict] = {}
    for check in eligibility_checks:
        latest_by_client.setdefault(check["client_id"], check)
    for client_id, check in latest_by_client.items():
        if check["coverage_status"] == "failed":
            pools["eligibility_failed"].append(
                {
                    "client_id": client_id,
                    "severity": AlertSeverity.HIGH,
                    "explanation": f"Latest eligibility check with {check['payer']} failed: {check.get('failure_reason') or 'reason not recorded'}.",
                    "recommended_action": "Re-verify eligibility with the payer and update the client record.",
                }
            )
        term = _parse_date(check.get("termination_date"))
        if term and today <= term <= today + timedelta(days=COVERAGE_ENDING_WINDOW_DAYS):
            days = (term - today).days
            pools["coverage_ending_soon"].append(
                {
                    "client_id": client_id,
                    "severity": AlertSeverity.HIGH if days <= 10 else AlertSeverity.MEDIUM,
                    "explanation": f"Coverage with {check['payer']} ends in {days} day(s) ({term.isoformat()}).",
                    "recommended_action": "Confirm renewal or transition plan with the client before coverage lapses.",
                }
            )

    active_auths_by_client: dict[str, set[str]] = defaultdict(set)
    for auth in authorizations:
        if auth["status"] in ("active", "pending"):
            active_auths_by_client[auth["client_id"]].add(str(auth["_id"]))
        exp = _parse_date(auth["expiration_date"])
        if auth["status"] in ("active", "pending") and exp and today <= exp <= today + timedelta(days=EXPIRING_WINDOW_DAYS):
            days = (exp - today).days
            pools["authorization_expiring"].append(
                {
                    "client_id": auth["client_id"],
                    "severity": AlertSeverity.CRITICAL if days <= 3 else AlertSeverity.HIGH,
                    "explanation": f"Authorization {auth['authorization_number']} ({auth['payer']}) expires in {days} day(s).",
                    "recommended_action": "Submit a renewal request to the payer before expiration.",
                }
            )
        usage = auth["units_used"] / auth["units_approved"] if auth["units_approved"] else 0
        if auth["status"] == "exhausted" or usage >= UNITS_EXHAUSTED_THRESHOLD:
            pct = round(100 * usage)
            pools["authorization_units_exhausted"].append(
                {
                    "client_id": auth["client_id"],
                    "severity": AlertSeverity.HIGH,
                    "explanation": f"Authorization {auth['authorization_number']} has used {pct}% of approved units ({auth['units_used']}/{auth['units_approved']}).",
                    "recommended_action": "Request additional units or schedule a new authorization before service is interrupted.",
                }
            )

    for appt in appointments:
        if appt["status"] != "scheduled":
            continue
        appt_dt = appt["appointment_datetime"]
        if isinstance(appt_dt, str) and appt_dt <= now_iso:
            continue
        has_valid_auth = appt.get("authorization_id") in active_auths_by_client.get(appt["client_id"], set())
        if not has_valid_auth:
            pools["appointment_without_authorization"].append(
                {
                    "client_id": appt["client_id"],
                    "severity": AlertSeverity.CRITICAL,
                    "explanation": f"Upcoming {appt['service_type']} appointment on {appt_dt[:10]} has no linked authorization.",
                    "recommended_action": "Obtain or link a valid authorization before the appointment occurs.",
                }
            )

    for task in tasks:
        if task.get("client_id") and task["status"] != "completed":
            due = _parse_date(task["due_date"])
            if due and due < today:
                pools["overdue_task"].append(
                    {
                        "client_id": task["client_id"],
                        "severity": AlertSeverity.MEDIUM if (today - due).days < 14 else AlertSeverity.HIGH,
                        "explanation": f"Task '{task['title']}' was due {due.isoformat()} and is still {task['status']}.",
                        "recommended_action": "Reassign or complete the overdue task as soon as possible.",
                    }
                )

    issue_counts: dict[str, int] = defaultdict(int)
    for candidates in pools.values():
        for c in candidates:
            issue_counts[c["client_id"]] += 1
    for client_id, count in issue_counts.items():
        if count >= MULTIPLE_ISSUES_THRESHOLD:
            pools["multiple_unresolved_issues"].append(
                {
                    "client_id": client_id,
                    "severity": AlertSeverity.CRITICAL,
                    "explanation": f"Client has {count} concurrent open operational issues across eligibility, authorization, and scheduling.",
                    "recommended_action": "Escalate to a case review; assign a single owner to coordinate resolution.",
                }
            )

    return pools


async def generate_alerts(db: AsyncIOMotorDatabase) -> AlertGenerationResult:
    repository = AlertRepository(db["alerts"])
    pools = await _candidates(db)

    created = 0
    skipped = 0
    created_by_type: dict[str, int] = defaultdict(int)
    seen_this_run: set[tuple[str, str]] = set()

    for alert_type, candidates in pools.items():
        for candidate in candidates:
            key = (candidate["client_id"], alert_type)
            if key in seen_this_run:
                continue
            seen_this_run.add(key)

            if await repository.find_active_duplicate(candidate["client_id"], alert_type):
                skipped += 1
                continue

            created_alert = await repository.create(
                {
                    "client_id": candidate["client_id"],
                    "alert_type": alert_type,
                    "severity": candidate["severity"].value,
                    "explanation": candidate["explanation"],
                    "recommended_action": candidate["recommended_action"],
                    "assigned_employee_id": None,
                    "status": AlertStatus.OPEN.value,
                    "resolution_notes": None,
                    "resolved_at": None,
                }
            )
            await record_audit(
                db,
                user=GENERATED_BY_USER,
                action="create",
                entity_type="alert",
                entity_id=created_alert["id"],
                new_value=created_alert,
            )
            created += 1
            created_by_type[alert_type] += 1

    total_clients = await db["clients"].count_documents({})
    return AlertGenerationResult(
        scanned_clients=total_clients,
        alerts_created=created,
        alerts_skipped_as_duplicate=skipped,
        created_by_type=dict(created_by_type),
    )
