"""Explainable, rule-based operational risk score.

Deliberately not machine learning: every point is traceable to a named,
documented factor so an operations user can see exactly why a client
scored the way they did. This is the one place the scoring rules live —
both the API's GET /clients/{id}/risk endpoint and the alert-generation
service (app/services/alert_generation.py) read from the same signal
functions here, so the score and the alerts it explains can never
disagree with each other.

Weights were chosen so no single factor dominates the score, and the
four bands split the resulting range into roughly even quartiles.
"""
from datetime import UTC, date, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.risk import RiskFactorDetail, RiskScore

AUTHORIZATION_EXPIRING_WINDOW_DAYS = 14
COVERAGE_ENDING_WINDOW_DAYS = 30
UNITS_EXHAUSTED_THRESHOLD = 0.9
MULTIPLE_ALERTS_THRESHOLD = 2

WEIGHTS = {
    "appointment_without_authorization": 25,
    "eligibility_failed": 20,
    "authorization_expiring": 15,
    "authorization_units_exhausted": 15,
    "coverage_ending_soon": 15,
    "multiple_unresolved_alerts": 15,
    "overdue_task": 15,
}

BAND_THRESHOLDS = [(75, "Critical"), (50, "High"), (25, "Medium"), (0, "Low")]


def _band_for(score: int) -> str:
    for threshold, band in BAND_THRESHOLDS:
        if score >= threshold:
            return band
    return "Low"


def _parse_date(value) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value) if isinstance(value, str) else value


async def _latest_eligibility_check(db: AsyncIOMotorDatabase, client_id: str) -> dict | None:
    return await db["eligibility_checks"].find_one({"client_id": client_id}, sort=[("check_date", -1)])


async def compute_client_risk(db: AsyncIOMotorDatabase, client_id: str) -> RiskScore:
    today = date.today()
    factors: list[RiskFactorDetail] = []

    # --- Latest eligibility check failed / coverage ending soon ---
    latest_check = await _latest_eligibility_check(db, client_id)
    if latest_check and latest_check.get("coverage_status") == "failed":
        factors.append(
            RiskFactorDetail(
                code="eligibility_failed",
                label="Latest eligibility check failed",
                points=WEIGHTS["eligibility_failed"],
                detail=f"With {latest_check['payer']}: {latest_check.get('failure_reason') or 'reason not recorded'}.",
            )
        )
    if latest_check and latest_check.get("termination_date"):
        term = _parse_date(latest_check["termination_date"])
        if term and today <= term <= date.fromordinal(today.toordinal() + COVERAGE_ENDING_WINDOW_DAYS):
            factors.append(
                RiskFactorDetail(
                    code="coverage_ending_soon",
                    label="Coverage termination date approaching",
                    points=WEIGHTS["coverage_ending_soon"],
                    detail=f"Coverage with {latest_check['payer']} ends {term.isoformat()}.",
                )
            )

    # --- Authorizations: expiring soon / units nearly exhausted ---
    authorizations = await db["authorizations"].find({"client_id": client_id}).to_list(length=None)
    active_or_pending_auth_ids = set()
    for auth in authorizations:
        if auth["status"] in ("active", "pending"):
            active_or_pending_auth_ids.add(str(auth["_id"]))
            exp = _parse_date(auth["expiration_date"])
            if exp and today <= exp <= date.fromordinal(today.toordinal() + AUTHORIZATION_EXPIRING_WINDOW_DAYS):
                factors.append(
                    RiskFactorDetail(
                        code="authorization_expiring",
                        label="Authorization expires within 14 days",
                        points=WEIGHTS["authorization_expiring"],
                        detail=f"{auth['authorization_number']} ({auth['payer']}) expires {exp.isoformat()}.",
                    )
                )
                break  # one contribution per factor, regardless of how many authorizations qualify
    for auth in authorizations:
        usage = auth["units_used"] / auth["units_approved"] if auth["units_approved"] else 0
        if auth["status"] == "exhausted" or usage >= UNITS_EXHAUSTED_THRESHOLD:
            factors.append(
                RiskFactorDetail(
                    code="authorization_units_exhausted",
                    label="Authorization units nearly exhausted",
                    points=WEIGHTS["authorization_units_exhausted"],
                    detail=f"{auth['authorization_number']} has used {auth['units_used']}/{auth['units_approved']} units.",
                )
            )
            break

    # --- Upcoming appointment without a valid (active) authorization ---
    now_iso = datetime.now(UTC).isoformat()
    upcoming = await db["appointments"].find_one(
        {"client_id": client_id, "status": "scheduled", "appointment_datetime": {"$gt": now_iso}}
    )
    if upcoming and (
        not upcoming.get("authorization_id") or upcoming["authorization_id"] not in active_or_pending_auth_ids
    ):
        factors.append(
            RiskFactorDetail(
                code="appointment_without_authorization",
                label="Upcoming appointment without a valid authorization",
                points=WEIGHTS["appointment_without_authorization"],
                detail=f"{upcoming['service_type']} appointment on {upcoming['appointment_datetime'][:10]} has no active authorization linked.",
            )
        )

    # --- Multiple unresolved alerts ---
    unresolved_alerts = await db["alerts"].count_documents({"client_id": client_id, "status": {"$ne": "resolved"}})
    if unresolved_alerts >= MULTIPLE_ALERTS_THRESHOLD:
        factors.append(
            RiskFactorDetail(
                code="multiple_unresolved_alerts",
                label="Multiple unresolved alerts",
                points=WEIGHTS["multiple_unresolved_alerts"],
                detail=f"{unresolved_alerts} alerts currently open or in progress.",
            )
        )

    # --- Overdue operational task ---
    overdue_task = await db["tasks"].find_one(
        {"client_id": client_id, "status": {"$ne": "completed"}, "due_date": {"$lt": today.isoformat()}}
    )
    if overdue_task:
        factors.append(
            RiskFactorDetail(
                code="overdue_task",
                label="Overdue operational task",
                points=WEIGHTS["overdue_task"],
                detail=f"'{overdue_task['title']}' was due {overdue_task['due_date']}.",
            )
        )

    score = min(100, sum(f.points for f in factors))
    return RiskScore(client_id=client_id, score=score, band=_band_for(score), factors=factors)
