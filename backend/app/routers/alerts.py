from fastapi import APIRouter, Depends

from app.core.roles import Role, get_current_user_name, require_role
from app.models.alert import AlertSeverity, AlertStatus
from app.repositories.alerts import AlertRepository, get_alert_repository
from app.schemas.alert import AlertCreate, AlertRead, AlertUpdate
from app.schemas.common import ItemResponse, ListParams, ListResponse, PageMeta
from app.services.alerts import AlertService

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


def get_alert_service(repository: AlertRepository = Depends(get_alert_repository)) -> AlertService:
    return AlertService(repository)


@router.get("", response_model=ListResponse[AlertRead], dependencies=[Depends(require_role(*Role))])
async def list_alerts(
    client_id: str | None = None,
    status: AlertStatus | None = None,
    severity: AlertSeverity | None = None,
    assigned_employee_id: str | None = None,
    params: ListParams = Depends(),
    service: AlertService = Depends(get_alert_service),
):
    docs, total = await service.list(
        client_id=client_id, status=status, severity=severity, assigned_employee_id=assigned_employee_id,
        page=params.page, page_size=params.page_size, sort_field=params.sort_field, sort_direction=params.sort_direction,
    )
    return ListResponse(data=docs, meta=PageMeta(page=params.page, page_size=params.page_size, total=total))


@router.get("/{alert_id}", response_model=ItemResponse[AlertRead], dependencies=[Depends(require_role(*Role))])
async def get_alert(alert_id: str, service: AlertService = Depends(get_alert_service)):
    return ItemResponse(data=await service.get(alert_id))


@router.post(
    "", response_model=ItemResponse[AlertRead], status_code=201,
    dependencies=[Depends(require_role(Role.OPERATIONS_MANAGER))],
)
async def create_alert(
    payload: AlertCreate,
    user: str = Depends(get_current_user_name),
    service: AlertService = Depends(get_alert_service),
):
    return ItemResponse(data=await service.create(payload, user=user))


@router.patch("/{alert_id}", response_model=ItemResponse[AlertRead], dependencies=[Depends(require_role(*Role))])
async def update_alert(
    alert_id: str,
    payload: AlertUpdate,
    user: str = Depends(get_current_user_name),
    service: AlertService = Depends(get_alert_service),
):
    return ItemResponse(data=await service.update(alert_id, payload, user=user))
