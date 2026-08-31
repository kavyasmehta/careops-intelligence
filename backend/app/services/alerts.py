from datetime import UTC, datetime

from app.core.errors import ConflictError, NotFoundError
from app.db.mongo import get_database
from app.models.alert import AlertStatus
from app.repositories.alerts import AlertRepository
from app.schemas.alert import AlertCreate, AlertUpdate
from app.services.audit import record_audit


class AlertService:
    def __init__(self, repository: AlertRepository):
        self.repository = repository

    async def list(self, *, client_id, status, severity, assigned_employee_id, page, page_size, sort_field, sort_direction):
        filter_ = self.repository.build_filter(
            client_id=client_id, status=status, severity=severity, assigned_employee_id=assigned_employee_id
        )
        return await self.repository.list(
            filter_, page=page, page_size=page_size, sort_field=sort_field, sort_direction=sort_direction
        )

    async def get(self, alert_id: str) -> dict:
        doc = await self.repository.get(alert_id)
        if not doc:
            raise NotFoundError(f"Alert {alert_id} not found")
        return doc

    async def create(self, payload: AlertCreate, *, user: str) -> dict:
        # A client can only have one active (non-resolved) alert of a given
        # type at a time — this is the "no duplicate active alerts" rule
        # from the spec, enforced here so it applies whether the alert is
        # created manually or by the automated rule engine (Phase 8).
        duplicate = await self.repository.find_active_duplicate(payload.client_id, payload.alert_type.value)
        if duplicate:
            raise ConflictError(
                f"An active '{payload.alert_type.value}' alert already exists for client {payload.client_id}"
            )
        doc = await self.repository.create(payload.model_dump(mode="json"))
        await record_audit(
            get_database(), user=user, action="create", entity_type="alert", entity_id=doc["id"], new_value=doc
        )
        return doc

    async def update(self, alert_id: str, payload: AlertUpdate, *, user: str) -> dict:
        existing = await self.get(alert_id)
        changes = payload.model_dump(mode="json", exclude_unset=True)
        if changes.get("status") == AlertStatus.RESOLVED.value and existing["status"] != AlertStatus.RESOLVED.value:
            changes["resolved_at"] = datetime.now(UTC).isoformat()
        updated = await self.repository.update(alert_id, changes)
        if not updated:
            raise NotFoundError(f"Alert {alert_id} not found")
        await record_audit(
            get_database(), user=user, action="update", entity_type="alert",
            entity_id=alert_id, previous_value=existing, new_value=updated,
        )
        return updated
