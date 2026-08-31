"""
Reproducible synthetic-data seed for CareOps Intelligence's MongoDB collections.

Safe to rerun: clears the target collections first, then regenerates
everything from a fixed random seed, so repeated runs produce the same
shape and distribution of data (only fresh ObjectIds differ).

Problem scenarios are generated deliberately, not left to chance: failed
eligibility checks, expired/exhausted authorizations, appointments
missing a valid authorization, overdue tasks, coverage ending soon, and
uneven employee caseloads. Alerts are then derived FROM those real
conditions (not random) so the seeded alert queue is internally
consistent — an alert always points at an actual underlying record.
"""
import os
import random
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from faker import Faker
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_data import EMPLOYEES, PAYERS, PROVIDERS, SERVICE_TYPES, TEAMS  # noqa: E402
from risk_conditions import compute_multiple_issues_pool, compute_risk_pools  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SEED = 42
random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27018")
MONGO_DB = os.getenv("MONGO_DB", "careops")

N_CLIENTS = 250
N_ELIGIBILITY = 1000
N_AUTHORIZATIONS = 500
N_APPOINTMENTS = 1000
N_TASKS = 500
N_CASE_NOTES = 1000
ALERT_TARGETS = {
    "eligibility_failed": 70,
    "authorization_expiring": 60,
    "appointment_without_authorization": 50,
    "authorization_units_exhausted": 40,
    "coverage_ending_soon": 40,
    "overdue_task": 30,
    "multiple_unresolved_issues": 10,
}

TODAY = date.today()

# Deliberately uneven client-caseload weights across the 8 non-manager
# employees (index-aligned with CASELOAD_EMPLOYEES below) — produces the
# "uneven employee workload" scenario the spec calls for.
CASELOAD_EMPLOYEES = [e for e in EMPLOYEES if e["role"] != "operations_manager"]
CASELOAD_WEIGHTS = [6, 2, 5, 1, 6, 1, 4, 2]

FAILURE_REASONS = [
    "Member ID not found",
    "Coverage terminated prior to service date",
    "Plan not active for requested service",
    "Payer system error during verification",
    "Client ineligible for requested service type",
]

TASK_TEMPLATES = [
    "Follow up on failed eligibility check",
    "Verify authorization renewal status",
    "Confirm upcoming appointment with client",
    "Review recent case notes for follow-up items",
    "Update client contact information",
    "Reconcile authorization units used",
    "Contact payer regarding coverage termination",
    "Schedule missing authorization request",
]

NOTE_TAGS = ["intake", "follow-up", "eligibility", "authorization", "appointment", "risk", "general", "billing"]


def iso(value) -> str:
    return value.isoformat()


def random_datetime_within(days_back: int, days_forward: int = 0) -> datetime:
    delta = random.randint(-days_back, days_forward)
    return datetime.now(UTC) + timedelta(days=delta, hours=random.randint(0, 23))


def random_date_within(days_back: int, days_forward: int = 0) -> date:
    delta = random.randint(-days_back, days_forward)
    return TODAY + timedelta(days=delta)


def timestamps(created_days_ago: int) -> dict:
    created = datetime.now(UTC) - timedelta(days=created_days_ago, hours=random.randint(0, 23))
    return {"created_at": created, "updated_at": created}


# ---------------------------------------------------------------------------
# Reference collections
# ---------------------------------------------------------------------------


def seed_users(db) -> list[dict]:
    docs = []
    for emp in EMPLOYEES:
        doc = {"name": emp["name"], "role": emp["role"], "team_id": emp["team"]}
        doc.update(timestamps(created_days_ago=365))
        docs.append(doc)
    db["users"].insert_many(docs)
    return docs


def seed_clients(db, employees: list[dict]) -> list[dict]:
    caseload_ids = [next(e["_id"] for e in employees if e["name"] == c["name"]) for c in CASELOAD_EMPLOYEES]
    docs = []
    for i in range(N_CLIENTS):
        idx = random.choices(range(len(caseload_ids)), weights=CASELOAD_WEIGHTS, k=1)[0]
        employee_id = str(caseload_ids[idx])
        team_id = CASELOAD_EMPLOYEES[idx]["team"]
        first_name, last_name = fake.first_name(), fake.last_name()
        doc = {
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": iso(fake.date_of_birth(minimum_age=1, maximum_age=95)),
            "member_id": f"MBR-{100000 + i}",
            "email": fake.unique.email(),
            "phone": fake.numerify("###-###-####"),
            "address": {
                "line1": fake.street_address(),
                "city": fake.city(),
                "state": fake.state_abbr(),
                "zip": fake.zipcode(),
            },
            "assigned_team_id": team_id,
            "assigned_employee_id": employee_id,
            "status": random.choices(
                ["active", "pending", "inactive", "discharged"], weights=[70, 12, 10, 8]
            )[0],
        }
        doc.update(timestamps(created_days_ago=random.randint(30, 400)))
        docs.append(doc)
    db["clients"].insert_many(docs)
    return docs


def seed_eligibility(db, clients: list[dict]) -> list[dict]:
    docs = []
    for _ in range(N_ELIGIBILITY):
        c = random.choice(clients)
        status = random.choices(["active", "failed", "pending", "inactive"], weights=[62, 18, 12, 8])[0]
        check_date = random_datetime_within(days_back=180)
        effective = check_date.date() - timedelta(days=random.randint(30, 400))
        ending_soon = random.random() < 0.12
        termination = (
            TODAY + timedelta(days=random.randint(-5, 30)) if ending_soon else
            (check_date.date() + timedelta(days=random.randint(200, 500)) if random.random() < 0.3 else None)
        )
        doc = {
            "client_id": str(c["_id"]),
            "payer": random.choice(PAYERS),
            "check_date": iso(check_date),
            "coverage_status": status,
            "effective_date": iso(effective),
            "termination_date": iso(termination) if termination else None,
            "plan_name": f"{fake.word().capitalize()} {random.choice(['Plus', 'Advantage', 'Essential', 'Complete'])}",
            "failure_reason": random.choice(FAILURE_REASONS) if status == "failed" else None,
            "source": random.choices(["clearinghouse", "payer_portal", "manual"], weights=[60, 30, 10])[0],
            "processed": True,
        }
        doc.update(timestamps(created_days_ago=(datetime.now(UTC) - check_date).days))
        docs.append(doc)
    db["eligibility_checks"].insert_many(docs)
    return docs


def seed_authorizations(db, clients: list[dict]) -> list[dict]:
    docs = []
    for i in range(N_AUTHORIZATIONS):
        c = random.choice(clients)
        status = random.choices(
            ["active", "pending", "expired", "exhausted", "denied"], weights=[42, 15, 15, 18, 10]
        )[0]
        units_approved = random.randint(4, 40)

        if status == "exhausted":
            units_used = units_approved
        elif status == "denied":
            units_used = 0
        elif status in ("active", "pending"):
            units_used = random.randint(0, int(units_approved * 0.7))
        else:  # expired
            units_used = random.randint(0, units_approved)

        if status == "expired":
            expiration = TODAY - timedelta(days=random.randint(1, 150))
            effective = expiration - timedelta(days=random.randint(60, 200))
        elif status == "active" and random.random() < 0.25:
            # ~25% of active authorizations expire soon -> feeds the
            # authorization_expiring alert scenario.
            expiration = TODAY + timedelta(days=random.randint(1, 14))
            effective = TODAY - timedelta(days=random.randint(30, 120))
        else:
            effective = TODAY - timedelta(days=random.randint(0, 120))
            expiration = effective + timedelta(days=random.randint(60, 240))

        doc = {
            "client_id": str(c["_id"]),
            "payer": random.choice(PAYERS),
            "authorization_number": f"AUTH-{20000 + i}",
            "service_type": random.choice(SERVICE_TYPES),
            "units_approved": units_approved,
            "units_used": units_used,
            "effective_date": iso(effective),
            "expiration_date": iso(expiration),
            "status": status,
        }
        doc.update(timestamps(created_days_ago=(TODAY - effective).days if effective <= TODAY else 0))
        docs.append(doc)
    db["authorizations"].insert_many(docs)
    return docs


def seed_appointments(db, clients: list[dict], authorizations: list[dict]) -> list[dict]:
    auths_by_client: dict[str, list[dict]] = {}
    for a in authorizations:
        auths_by_client.setdefault(a["client_id"], []).append(a)

    docs = []
    for _ in range(N_APPOINTMENTS):
        c = random.choice(clients)
        client_id = str(c["_id"])
        is_future = random.random() < 0.45
        appt_dt = random_datetime_within(days_back=0 if is_future else 150, days_forward=60 if is_future else 0)

        if is_future:
            status = random.choices(["scheduled", "cancelled"], weights=[92, 8])[0]
        else:
            status = random.choices(["completed", "cancelled", "no_show"], weights=[72, 15, 13])[0]

        provider = random.choice(PROVIDERS)
        client_auths = auths_by_client.get(client_id, [])
        authorization_id = None
        if client_auths and random.random() < 0.75:
            preferred = [a for a in client_auths if a["status"] in ("active", "pending")]
            chosen = random.choice(preferred) if preferred else random.choice(client_auths)
            authorization_id = str(chosen["_id"])
        # else: intentionally left without an authorization — feeds the
        # appointment_without_authorization alert scenario, especially
        # meaningful for future/scheduled appointments.

        doc = {
            "client_id": client_id,
            "appointment_datetime": iso(appt_dt),
            "service_type": provider["specialty"],
            "provider": provider["name"],
            "location": f"{fake.city()} Care Center",
            "status": status,
            "authorization_id": authorization_id,
        }
        doc.update(timestamps(created_days_ago=max((datetime.now(UTC) - appt_dt).days, 0) + random.randint(1, 10)))
        docs.append(doc)
    db["appointments"].insert_many(docs)
    return docs


def seed_tasks(db, clients: list[dict], employees: list[dict]) -> list[dict]:
    docs = []
    for _ in range(N_TASKS):
        c = random.choice(clients) if random.random() < 0.9 else None
        employee = random.choice(employees)
        due = random_date_within(days_back=60, days_forward=30)
        status = random.choices(["open", "in_progress", "completed"], weights=[40, 25, 35])[0]
        doc = {
            "title": random.choice(TASK_TEMPLATES),
            "description": fake.sentence(nb_words=12),
            "client_id": str(c["_id"]) if c else None,
            "assigned_employee_id": str(employee["_id"]),
            "priority": random.choices(["low", "medium", "high", "urgent"], weights=[25, 40, 25, 10])[0],
            "due_date": iso(due),
            "status": status,
            "completed_at": iso(random_datetime_within(days_back=30)) if status == "completed" else None,
        }
        doc.update(timestamps(created_days_ago=random.randint(1, 90)))
        docs.append(doc)
    db["tasks"].insert_many(docs)
    return docs


def seed_case_notes(db, clients: list[dict], employees: list[dict]) -> list[dict]:
    docs = []
    for _ in range(N_CASE_NOTES):
        c = random.choice(clients)
        employee = random.choice(employees)
        doc = {
            "client_id": str(c["_id"]),
            "author": employee["name"],
            "note_text": fake.paragraph(nb_sentences=3),
            "tags": random.sample(NOTE_TAGS, k=random.randint(1, 3)),
        }
        doc.update(timestamps(created_days_ago=random.randint(0, 180)))
        docs.append(doc)
    db["case_notes"].insert_many(docs)
    return docs


# ---------------------------------------------------------------------------
# Alerts — derived from the real problem conditions generated above
# ---------------------------------------------------------------------------


def seed_alerts(db, pools: dict[str, list[dict]], employees: list[dict]) -> list[dict]:
    auth_specialists = [e for e in employees if e["role"] == "authorization_specialist"]
    intake_specialists = [e for e in employees if e["role"] == "intake_specialist"]
    ops_managers = [e for e in employees if e["role"] == "operations_manager"]

    def assignee_for(alert_type: str) -> str:
        if alert_type in ("authorization_expiring", "authorization_units_exhausted"):
            return str(random.choice(auth_specialists)["_id"])
        if alert_type == "multiple_unresolved_issues":
            return str(random.choice(ops_managers)["_id"])
        return str(random.choice(intake_specialists)["_id"])

    docs = []
    seen: set[tuple[str, str]] = set()
    for alert_type, target in ALERT_TARGETS.items():
        candidates = pools[alert_type][:]
        random.shuffle(candidates)
        created = 0
        for candidate in candidates:
            if created >= target:
                break
            key = (candidate["client_id"], alert_type)
            if key in seen:
                continue
            seen.add(key)
            status = random.choices(["open", "in_progress", "resolved"], weights=[55, 20, 25])[0]
            resolved_at = iso(random_datetime_within(days_back=20)) if status == "resolved" else None
            doc = {
                "client_id": candidate["client_id"],
                "alert_type": alert_type,
                "severity": candidate["severity"],
                "explanation": candidate["explanation"],
                "recommended_action": candidate["recommended_action"],
                "assigned_employee_id": assignee_for(alert_type),
                "status": status,
                "resolution_notes": "Resolved after follow-up with client and payer." if status == "resolved" else None,
                "resolved_at": resolved_at,
            }
            doc.update(timestamps(created_days_ago=random.randint(1, 30)))
            docs.append(doc)
            created += 1
    if docs:
        db["alerts"].insert_many(docs)
    return docs


# ---------------------------------------------------------------------------


def main():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]

    print(f"Connected to {MONGO_URI}/{MONGO_DB}")
    print("Clearing existing seeded collections...")
    for name in [
        "users", "clients", "eligibility_checks", "authorizations",
        "appointments", "alerts", "tasks", "case_notes",
    ]:
        db[name].delete_many({})

    print("Seeding users...")
    users = seed_users(db)

    print(f"Seeding {N_CLIENTS} clients...")
    clients = seed_clients(db, users)

    print(f"Seeding {N_ELIGIBILITY} eligibility checks...")
    eligibility_checks = seed_eligibility(db, clients)

    print(f"Seeding {N_AUTHORIZATIONS} authorizations...")
    authorizations = seed_authorizations(db, clients)

    print(f"Seeding {N_APPOINTMENTS} appointments...")
    appointments = seed_appointments(db, clients, authorizations)

    print(f"Seeding {N_TASKS} tasks...")
    tasks = seed_tasks(db, clients, users)

    print(f"Seeding {N_CASE_NOTES} case notes...")
    seed_case_notes(db, clients, users)

    print("Deriving alert candidates from seeded problem scenarios...")
    pools = compute_risk_pools(clients, eligibility_checks, authorizations, appointments, tasks)
    pools["multiple_unresolved_issues"] = compute_multiple_issues_pool(pools)
    alerts = seed_alerts(db, pools, users)

    print("\n--- Seed summary ---")
    for name in [
        "users", "clients", "eligibility_checks", "authorizations",
        "appointments", "tasks", "case_notes", "alerts",
    ]:
        print(f"  {name}: {db[name].count_documents({})}")

    print("\n--- Problem-scenario counts (data validation) ---")
    print(f"  failed eligibility checks: {db['eligibility_checks'].count_documents({'coverage_status': 'failed'})}")
    print(f"  expired authorizations: {db['authorizations'].count_documents({'status': 'expired'})}")
    print(f"  exhausted authorizations: {db['authorizations'].count_documents({'status': 'exhausted'})}")
    print(f"  appointments without authorization: {db['appointments'].count_documents({'authorization_id': None})}")
    print(f"  overdue open/in-progress tasks: {sum(1 for t in tasks if t['status'] != 'completed' and date.fromisoformat(t['due_date']) < TODAY)}")
    print(f"  alerts by type: {[(t, db['alerts'].count_documents({'alert_type': t})) for t in ALERT_TARGETS]}")

    caseload = {}
    for c in clients:
        caseload[c["assigned_employee_id"]] = caseload.get(c["assigned_employee_id"], 0) + 1
    print(f"  client caseload spread (min/max per employee): {min(caseload.values())} / {max(caseload.values())}")

    client.close()
    print("\nMongoDB seed complete.")


if __name__ == "__main__":
    main()
