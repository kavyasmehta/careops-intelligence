from typing import Any

from app.db.mongo import get_database
from app.repositories.base import RepositoryBase


class AuditLogRepository(RepositoryBase):
    @staticmethod
    def build_filter(*, entity_type: str | None, entity_id: str | None) -> dict[str, Any]:
        filter_: dict[str, Any] = {}
        if entity_type:
            filter_["entity_type"] = entity_type
        if entity_id:
            filter_["entity_id"] = entity_id
        return filter_


def get_audit_log_repository() -> AuditLogRepository:
    return AuditLogRepository(get_database()["audit_logs"])
