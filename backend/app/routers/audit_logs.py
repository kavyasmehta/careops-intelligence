from fastapi import APIRouter, Depends, Query

from app.core.roles import Role, require_role
from app.repositories.audit_logs import AuditLogRepository, get_audit_log_repository
from app.schemas.audit_log import AuditLogRead
from app.schemas.common import ListResponse, PageMeta
from app.services.audit_logs import AuditLogService

router = APIRouter(prefix="/api/v1/audit-logs", tags=["audit-logs"])


def get_audit_log_service(repository: AuditLogRepository = Depends(get_audit_log_repository)) -> AuditLogService:
    return AuditLogService(repository)


@router.get("", response_model=ListResponse[AuditLogRead], dependencies=[Depends(require_role(*Role))])
async def list_audit_logs(
    entity_type: str | None = None,
    entity_id: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: AuditLogService = Depends(get_audit_log_service),
):
    docs, total = await service.list(entity_type=entity_type, entity_id=entity_id, page=page, page_size=page_size)
    return ListResponse(data=docs, meta=PageMeta(page=page, page_size=page_size, total=total))
