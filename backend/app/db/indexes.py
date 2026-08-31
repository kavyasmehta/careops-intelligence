"""Index creation, run once at application startup. Safe to call repeatedly
(`create_index`/`create_indexes` are no-ops if the index already exists),
which keeps the setup script and app startup both idempotent.

See docs/architecture.md for the reasoning behind each index choice.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    await db["clients"].create_index("member_id", unique=True)
    await db["clients"].create_index("assigned_employee_id")
    await db["clients"].create_index("status")
    await db["clients"].create_index("assigned_team_id")
    await db["clients"].create_index([("first_name", TEXT), ("last_name", TEXT)])

    await db["eligibility_checks"].create_index("client_id")
    await db["eligibility_checks"].create_index("coverage_status")
    await db["eligibility_checks"].create_index([("check_date", DESCENDING)])

    await db["authorizations"].create_index("client_id")
    await db["authorizations"].create_index("expiration_date")
    await db["authorizations"].create_index("status")
    await db["authorizations"].create_index([("status", ASCENDING), ("expiration_date", ASCENDING)])

    await db["appointments"].create_index("client_id")
    await db["appointments"].create_index("appointment_datetime")
    await db["appointments"].create_index("status")
    await db["appointments"].create_index("provider")

    await db["alerts"].create_index([("status", ASCENDING), ("severity", ASCENDING)])
    await db["alerts"].create_index("assigned_employee_id")
    await db["alerts"].create_index("client_id")
    await db["alerts"].create_index([("client_id", ASCENDING), ("alert_type", ASCENDING), ("status", ASCENDING)])

    await db["tasks"].create_index("status")
    await db["tasks"].create_index("due_date")
    await db["tasks"].create_index("assigned_employee_id")

    await db["case_notes"].create_index([("client_id", ASCENDING), ("created_at", DESCENDING)])

    await db["audit_logs"].create_index([("entity_type", ASCENDING), ("entity_id", ASCENDING)])
    await db["audit_logs"].create_index([("timestamp", DESCENDING)])

    await db["users"].create_index("role")
