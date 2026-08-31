"""Shared problem-condition detection, used by BOTH seed scripts.

seed_mongo.py turns these into Alert documents (with severity/explanation
text); seed_neo4j.py turns the same client sets into RiskFactor graph
nodes/edges. Keeping the detection logic in one place means the alert
queue and the graph's risk factors can never drift out of sync with
each other — they're two views of the same underlying conditions.
"""
from datetime import UTC, date, datetime, timedelta

TODAY = date.today()

RISK_CONDITION_TYPES = [
    "eligibility_failed",
    "coverage_ending_soon",
    "authorization_expiring",
    "authorization_units_exhausted",
    "appointment_without_authorization",
    "overdue_task",
]


def compute_risk_pools(clients, eligibility_checks, authorizations, appointments, tasks) -> dict[str, list[dict]]:
    """Returns, per condition type, a list of {client_id, severity, explanation, recommended_action}."""
    pools: dict[str, list[dict]] = {k: [] for k in RISK_CONDITION_TYPES}

    latest_eligibility: dict[str, dict] = {}
    for check in eligibility_checks:
        cid = check["client_id"]
        if cid not in latest_eligibility or check["check_date"] > latest_eligibility[cid]["check_date"]:
            latest_eligibility[cid] = check

    for cid, check in latest_eligibility.items():
        if check["coverage_status"] == "failed":
            pools["eligibility_failed"].append(
                {
                    "client_id": cid,
                    "severity": "high",
                    "explanation": f"Latest eligibility check with {check['payer']} failed: {check['failure_reason']}.",
                    "recommended_action": "Re-verify eligibility with the payer and update the client record.",
                }
            )
        if check["termination_date"]:
            term = date.fromisoformat(check["termination_date"])
            if TODAY <= term <= TODAY + timedelta(days=30):
                days = (term - TODAY).days
                pools["coverage_ending_soon"].append(
                    {
                        "client_id": cid,
                        "severity": "medium" if days > 10 else "high",
                        "explanation": f"Coverage with {check['payer']} ends in {days} day(s) ({check['termination_date']}).",
                        "recommended_action": "Confirm renewal or transition plan with the client before coverage lapses.",
                    }
                )

    for auth in authorizations:
        exp = date.fromisoformat(auth["expiration_date"])
        if auth["status"] in ("active", "pending") and TODAY <= exp <= TODAY + timedelta(days=14):
            days = (exp - TODAY).days
            pools["authorization_expiring"].append(
                {
                    "client_id": auth["client_id"],
                    "severity": "critical" if days <= 3 else "high",
                    "explanation": f"Authorization {auth['authorization_number']} ({auth['payer']}) expires in {days} day(s).",
                    "recommended_action": "Submit a renewal request to the payer before expiration.",
                }
            )
        if auth["status"] == "exhausted" or (
            auth["units_approved"] and auth["units_used"] / auth["units_approved"] >= 0.9
        ):
            pct = round(100 * auth["units_used"] / auth["units_approved"])
            pools["authorization_units_exhausted"].append(
                {
                    "client_id": auth["client_id"],
                    "severity": "high",
                    "explanation": f"Authorization {auth['authorization_number']} has used {pct}% of approved units ({auth['units_used']}/{auth['units_approved']}).",
                    "recommended_action": "Request additional units or schedule a new authorization before service is interrupted.",
                }
            )

    for appt in appointments:
        appt_date = appt["appointment_datetime"]
        if isinstance(appt_date, str):
            appt_date = datetime.fromisoformat(appt_date)
        if appt_date.tzinfo is None:
            appt_date = appt_date.replace(tzinfo=UTC)
        if appt["status"] == "scheduled" and appt["authorization_id"] is None and appt_date > datetime.now(UTC):
            pools["appointment_without_authorization"].append(
                {
                    "client_id": appt["client_id"],
                    "severity": "critical",
                    "explanation": f"Upcoming {appt['service_type']} appointment on {appt_date.date()} has no linked authorization.",
                    "recommended_action": "Obtain or link a valid authorization before the appointment occurs.",
                }
            )

    for task in tasks:
        if task["client_id"] and task["status"] != "completed":
            due = date.fromisoformat(task["due_date"])
            if due < TODAY:
                pools["overdue_task"].append(
                    {
                        "client_id": task["client_id"],
                        "severity": "medium" if (TODAY - due).days < 14 else "high",
                        "explanation": f"Task '{task['title']}' was due {due.isoformat()} and is still {task['status']}.",
                        "recommended_action": "Reassign or complete the overdue task as soon as possible.",
                    }
                )

    return pools


def compute_multiple_issues_pool(pools: dict[str, list[dict]], min_issues: int = 3) -> list[dict]:
    issue_counts: dict[str, int] = {}
    for candidates in pools.values():
        for candidate in candidates:
            issue_counts[candidate["client_id"]] = issue_counts.get(candidate["client_id"], 0) + 1
    return [
        {
            "client_id": cid,
            "severity": "critical",
            "explanation": f"Client has {count} concurrent open operational issues across eligibility, authorization, and scheduling.",
            "recommended_action": "Escalate to a case review; assign a single owner to coordinate resolution.",
        }
        for cid, count in issue_counts.items()
        if count >= min_issues
    ]
