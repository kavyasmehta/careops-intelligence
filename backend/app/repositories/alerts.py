from typing import Any

from app.db.mongo import get_database
from app.repositories.base import RepositoryBase


class AlertRepository(RepositoryBase):
    @staticmethod
    def build_filter(
        *, client_id: str | None, status: str | None, severity: str | None, assigned_employee_id: str | None
    ) -> dict[str, Any]:
        filter_: dict[str, Any] = {}
        if client_id:
            filter_["client_id"] = client_id
        if status:
            filter_["status"] = status
        if severity:
            filter_["severity"] = severity
        if assigned_employee_id:
            filter_["assigned_employee_id"] = assigned_employee_id
        return filter_

    async def find_active_duplicate(self, client_id: str, alert_type: str) -> dict | None:
        doc = await self.collection.find_one(
            {"client_id": client_id, "alert_type": alert_type, "status": {"$ne": "resolved"}}
        )
        return self.serialize(doc) if doc else None


def get_alert_repository() -> AlertRepository:
    return AlertRepository(get_database()["alerts"])
