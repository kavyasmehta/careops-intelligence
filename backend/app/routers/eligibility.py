from fastapi import APIRouter, Depends

from app.core.roles import Role, get_current_user_name, require_role
from app.models.eligibility import CoverageStatus
from app.repositories.eligibility import EligibilityRepository, get_eligibility_repository
from app.schemas.common import ItemResponse, ListParams, ListResponse, PageMeta
from app.schemas.eligibility import EligibilityCheckCreate, EligibilityCheckRead, EligibilityCheckUpdate
from app.services.eligibility import EligibilityService

router = APIRouter(prefix="/api/v1/eligibility-checks", tags=["eligibility"])


def get_eligibility_service(repository: EligibilityRepository = Depends(get_eligibility_repository)) -> EligibilityService:
    return EligibilityService(repository)


@router.get("", response_model=ListResponse[EligibilityCheckRead], dependencies=[Depends(require_role(*Role))])
async def list_eligibility_checks(
    client_id: str | None = None,
    coverage_status: CoverageStatus | None = None,
    params: ListParams = Depends(),
    service: EligibilityService = Depends(get_eligibility_service),
):
    docs, total = await service.list(
        client_id=client_id, coverage_status=coverage_status, page=params.page, page_size=params.page_size,
        sort_field=params.sort_field, sort_direction=params.sort_direction,
    )
    return ListResponse(data=docs, meta=PageMeta(page=params.page, page_size=params.page_size, total=total))


@router.get("/{check_id}", response_model=ItemResponse[EligibilityCheckRead], dependencies=[Depends(require_role(*Role))])
async def get_eligibility_check(check_id: str, service: EligibilityService = Depends(get_eligibility_service)):
    return ItemResponse(data=await service.get(check_id))


@router.post(
    "", response_model=ItemResponse[EligibilityCheckRead], status_code=201,
    dependencies=[Depends(require_role(Role.OPERATIONS_MANAGER, Role.INTAKE_SPECIALIST))],
)
async def create_eligibility_check(
    payload: EligibilityCheckCreate,
    user: str = Depends(get_current_user_name),
    service: EligibilityService = Depends(get_eligibility_service),
):
    return ItemResponse(data=await service.create(payload, user=user))


@router.patch(
    "/{check_id}", response_model=ItemResponse[EligibilityCheckRead],
    dependencies=[Depends(require_role(Role.OPERATIONS_MANAGER, Role.INTAKE_SPECIALIST))],
)
async def update_eligibility_check(
    check_id: str,
    payload: EligibilityCheckUpdate,
    user: str = Depends(get_current_user_name),
    service: EligibilityService = Depends(get_eligibility_service),
):
    return ItemResponse(data=await service.update(check_id, payload, user=user))
