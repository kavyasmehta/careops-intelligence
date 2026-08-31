from fastapi import APIRouter, Depends

from app.core.roles import Role, get_current_user_name, require_role
from app.models.appointment import AppointmentStatus
from app.repositories.appointments import AppointmentRepository, get_appointment_repository
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentUpdate
from app.schemas.common import ItemResponse, ListParams, ListResponse, PageMeta
from app.services.appointments import AppointmentService

router = APIRouter(prefix="/api/v1/appointments", tags=["appointments"])


def get_appointment_service(repository: AppointmentRepository = Depends(get_appointment_repository)) -> AppointmentService:
    return AppointmentService(repository)


@router.get("", response_model=ListResponse[AppointmentRead], dependencies=[Depends(require_role(*Role))])
async def list_appointments(
    client_id: str | None = None,
    status: AppointmentStatus | None = None,
    provider: str | None = None,
    service_type: str | None = None,
    params: ListParams = Depends(),
    service: AppointmentService = Depends(get_appointment_service),
):
    docs, total = await service.list(
        client_id=client_id, status=status, provider=provider, service_type=service_type,
        page=params.page, page_size=params.page_size, sort_field=params.sort_field, sort_direction=params.sort_direction,
    )
    return ListResponse(data=docs, meta=PageMeta(page=params.page, page_size=params.page_size, total=total))


@router.get("/{appointment_id}", response_model=ItemResponse[AppointmentRead], dependencies=[Depends(require_role(*Role))])
async def get_appointment(appointment_id: str, service: AppointmentService = Depends(get_appointment_service)):
    return ItemResponse(data=await service.get(appointment_id))


@router.post("", response_model=ItemResponse[AppointmentRead], status_code=201, dependencies=[Depends(require_role(*Role))])
async def create_appointment(
    payload: AppointmentCreate,
    user: str = Depends(get_current_user_name),
    service: AppointmentService = Depends(get_appointment_service),
):
    return ItemResponse(data=await service.create(payload, user=user))


@router.patch("/{appointment_id}", response_model=ItemResponse[AppointmentRead], dependencies=[Depends(require_role(*Role))])
async def update_appointment(
    appointment_id: str,
    payload: AppointmentUpdate,
    user: str = Depends(get_current_user_name),
    service: AppointmentService = Depends(get_appointment_service),
):
    return ItemResponse(data=await service.update(appointment_id, payload, user=user))
