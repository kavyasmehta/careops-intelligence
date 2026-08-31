from fastapi import APIRouter, Depends, Query

from app.core.roles import Role, get_current_user_name, require_role
from app.models.authorization import AuthorizationStatus
from app.repositories.authorizations import AuthorizationRepository, get_authorization_repository
from app.schemas.authorization import AuthorizationCreate, AuthorizationRead, AuthorizationUpdate
from app.schemas.common import ItemResponse, ListParams, ListResponse, PageMeta
from app.services.authorizations import AuthorizationService

router = APIRouter(prefix="/api/v1/authorizations", tags=["authorizations"])


def get_authorization_service(
    repository: AuthorizationRepository = Depends(get_authorization_repository),
) -> AuthorizationService:
    return AuthorizationService(repository)


@router.get("", response_model=ListResponse[AuthorizationRead], dependencies=[Depends(require_role(*Role))])
async def list_authorizations(
    client_id: str | None = None,
    status: AuthorizationStatus | None = None,
    params: ListParams = Depends(),
    service: AuthorizationService = Depends(get_authorization_service),
):
    docs, total = await service.list(
        client_id=client_id, status=status, page=params.page, page_size=params.page_size,
        sort_field=params.sort_field, sort_direction=params.sort_direction,
    )
    return ListResponse(data=docs, meta=PageMeta(page=params.page, page_size=params.page_size, total=total))


@router.get(
    "/expiring", response_model=ListResponse[AuthorizationRead], dependencies=[Depends(require_role(*Role))]
)
async def expiring_authorizations(
    within_days: int = Query(default=14, ge=1, le=365),
    service: AuthorizationService = Depends(get_authorization_service),
):
    docs = await service.expiring(within_days)
    return ListResponse(data=docs, meta=PageMeta(page=1, page_size=len(docs) or 1, total=len(docs)))


@router.get("/{authorization_id}", response_model=ItemResponse[AuthorizationRead], dependencies=[Depends(require_role(*Role))])
async def get_authorization(authorization_id: str, service: AuthorizationService = Depends(get_authorization_service)):
    return ItemResponse(data=await service.get(authorization_id))


@router.post(
    "", response_model=ItemResponse[AuthorizationRead], status_code=201,
    dependencies=[Depends(require_role(Role.OPERATIONS_MANAGER, Role.AUTHORIZATION_SPECIALIST))],
)
async def create_authorization(
    payload: AuthorizationCreate,
    user: str = Depends(get_current_user_name),
    service: AuthorizationService = Depends(get_authorization_service),
):
    return ItemResponse(data=await service.create(payload, user=user))


@router.patch(
    "/{authorization_id}", response_model=ItemResponse[AuthorizationRead],
    dependencies=[Depends(require_role(Role.OPERATIONS_MANAGER, Role.AUTHORIZATION_SPECIALIST))],
)
async def update_authorization(
    authorization_id: str,
    payload: AuthorizationUpdate,
    user: str = Depends(get_current_user_name),
    service: AuthorizationService = Depends(get_authorization_service),
):
    return ItemResponse(data=await service.update(authorization_id, payload, user=user))
