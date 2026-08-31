"""Writes an audit_logs entry for every create/update against a tracked entity.

Called from each entity's service layer (never from routers directly) so
that "what changed and who changed it" is captured consistently, in one
place, regardless of which endpoint triggered the write.
"""
from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


async def record_audit(
    db: AsyncIOMotorDatabase,
    *,
    user: str,
    action: str,
    entity_type: str,
    entity_id: str,
    previous_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
) -> None:
    await db["audit_logs"].insert_one(
        {
            "user": user,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.now(UTC),
            "previous_value": previous_value,
            "new_value": new_value,
        }
    )
