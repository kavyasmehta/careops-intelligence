from fastapi import APIRouter, Depends

from app.core.roles import Role, get_current_user_name, require_role
from app.models.client import ClientStatus
from app.repositories.clients import ClientRepository, get_client_repository
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.schemas.common import ItemResponse, ListParams, ListResponse, PageMeta
from app.services.clients import ClientService

router = APIRouter(prefix="/api/v1/clients", tags=["clients"])


def get_client_service(repository: ClientRepository = Depends(get_client_repository)) -> ClientService:
    return ClientService(repository)


@router.get("", response_model=ListResponse[ClientRead], dependencies=[Depends(require_role(*Role))])
async def list_clients(
    status: ClientStatus | None = None,
    team_id: str | None = None,
    employee_id: str | None = None,
    params: ListParams = Depends(),
    service: ClientService = Depends(get_client_service),
):
    docs, total = await service.list(
        status=status,
        team_id=team_id,
        employee_id=employee_id,
        q=params.q,
        page=params.page,
        page_size=params.page_size,
        sort_field=params.sort_field,
        sort_direction=params.sort_direction,
    )
    return ListResponse(data=docs, meta=PageMeta(page=params.page, page_size=params.page_size, total=total))


@router.get("/{client_id}", response_model=ItemResponse[ClientRead], dependencies=[Depends(require_role(*Role))])
async def get_client(client_id: str, service: ClientService = Depends(get_client_service)):
    return ItemResponse(data=await service.get(client_id))


@router.post(
    "",
    response_model=ItemResponse[ClientRead],
    status_code=201,
    dependencies=[Depends(require_role(Role.OPERATIONS_MANAGER, Role.INTAKE_SPECIALIST))],
)
async def create_client(
    payload: ClientCreate,
    user: str = Depends(get_current_user_name),
    service: ClientService = Depends(get_client_service),
):
    return ItemResponse(data=await service.create(payload, user=user))


@router.patch(
    "/{client_id}",
    response_model=ItemResponse[ClientRead],
    dependencies=[Depends(require_role(Role.OPERATIONS_MANAGER, Role.INTAKE_SPECIALIST))],
)
async def update_client(
    client_id: str,
    payload: ClientUpdate,
    user: str = Depends(get_current_user_name),
    service: ClientService = Depends(get_client_service),
):
    return ItemResponse(data=await service.update(client_id, payload, user=user))
