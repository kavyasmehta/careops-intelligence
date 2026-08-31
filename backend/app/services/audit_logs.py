from app.repositories.audit_logs import AuditLogRepository


class AuditLogService:
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    async def list(self, *, entity_type, entity_id, page, page_size):
        filter_ = self.repository.build_filter(entity_type=entity_type, entity_id=entity_id)
        # Audit trails are inherently chronological; always newest-first by
        # the actual event timestamp (these documents have no created_at).
        return await self.repository.list(
            filter_, page=page, page_size=page_size, sort_field="timestamp", sort_direction=-1
        )
