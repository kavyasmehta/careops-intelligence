from fastapi import APIRouter, Depends

from app.core.roles import Role, get_current_user_name, require_role
from app.repositories.case_notes import CaseNoteRepository, get_case_note_repository
from app.schemas.case_note import CaseNoteCreate, CaseNoteRead
from app.schemas.common import ItemResponse, ListParams, ListResponse, PageMeta
from app.services.case_notes import CaseNoteService

router = APIRouter(prefix="/api/v1/case-notes", tags=["case-notes"])


def get_case_note_service(repository: CaseNoteRepository = Depends(get_case_note_repository)) -> CaseNoteService:
    return CaseNoteService(repository)


@router.get("", response_model=ListResponse[CaseNoteRead], dependencies=[Depends(require_role(*Role))])
async def list_case_notes(
    client_id: str | None = None,
    params: ListParams = Depends(),
    service: CaseNoteService = Depends(get_case_note_service),
):
    docs, total = await service.list(
        client_id=client_id, page=params.page, page_size=params.page_size,
        sort_field=params.sort_field, sort_direction=params.sort_direction,
    )
    return ListResponse(data=docs, meta=PageMeta(page=params.page, page_size=params.page_size, total=total))


@router.post("", response_model=ItemResponse[CaseNoteRead], status_code=201, dependencies=[Depends(require_role(*Role))])
async def create_case_note(
    payload: CaseNoteCreate,
    user: str = Depends(get_current_user_name),
    service: CaseNoteService = Depends(get_case_note_service),
):
    return ItemResponse(data=await service.create(payload, user=user))
